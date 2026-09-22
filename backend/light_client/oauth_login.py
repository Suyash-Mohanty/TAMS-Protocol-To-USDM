#!/usr/bin/python

"""
    test_oauth_login.py

    This module contains utilities for obtaining, retrieving and storing an OAuth Access Token.

"""

import warnings

import os.path
import requests
import json
import time
import datetime
import logging
import sys
import urllib.request, urllib.parse, urllib.error
import weakref

from os.path import expanduser
from optparse import OptionParser
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from .encrypt import EncryptedConfigParser
from .synchronized import synchronized
from configparser import ConfigParser

CONFIG_DEFAULT = "DEFAULT"

# Fetch secret config
client_config = ConfigParser()
client_config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "client_config.ini"))


class TokenServer():
    """Class to represent the possible TokenServer an OAuth token can be requested from."""
    DEV = 2
    QA = 1
    PRD = 0

    @classmethod
    def name(cls, value):
        """Return the human-readable name of the supplied TokenServer instance.
        :param value: The TokenServer instance to get the name of.
        :returns: The supplied TokenServer's name."""
        if value == cls.DEV:
            return 'Dev'
        elif value == cls.QA:
            return 'QA'
        return ''


class Token():
    """An OAuth token instance."""

    def __init__(self):
        self.__token_type = None
        self.__access_token = None
        self.__expiry_timestamp = None
        self.__refresh_token = None
        self.__write_files = None
        self.__valid = True
        self.__header_formatter = None

    def __str__(self):
        return json.dumps({
            'token_type': self.__token_type,
            'access_token': 'set',
            'refresh_token': 'set',
            'expiry_timestamp': get_date_string(self.__expiry_timestamp),
            'write_files': self.__write_files,
            'valid': self.__valid
        })

    @property
    def token_type(self):
        """:returns: The OAuth token type."""
        return self.__token_type

    @token_type.setter
    def token_type(self, value):
        """Set the OAuth token type.
        :param value: The new OAuth token type."""
        self.__token_type = value

    @property
    def access_token(self):
        """:returns: The OAuth access token."""
        return self.__access_token

    @property
    def auth_header(self):
        """:returns: The OAuth access token."""
        if self.__header_formatter:
            return self.__header_formatter(self.__access_token)
        else:
            return 'Bearer %s' % self.__access_token

    @access_token.setter
    def access_token(self, value):
        """Set the OAuth access token.
        :param value: The new OAuth access token."""
        self.__access_token = value

    @property
    def expiry_timestamp(self):
        """:returns: The OAuth token expiry timestamp."""
        return self.__expiry_timestamp

    @expiry_timestamp.setter
    def expiry_timestamp(self, value):
        """Set the OAuth token expiry timestamp.
        :param value: The new OAuth token expiry timestamp."""
        self.__expiry_timestamp = value

    @property
    def refresh_token(self):
        """:returns: The OAuth refresh token."""
        return self.__refresh_token

    @refresh_token.setter
    def refresh_token(self, value):
        """Set the OAuth refresh token.
        :param value: The new OAuth refresh token."""
        self.__refresh_token = value

    @property
    def write_files(self):
        """:returns: Whether to write OAuth token to file."""
        return self.__write_files

    @write_files.setter
    def write_files(self, value):
        """Set whether to write OAuth token to file.
        :param value: Whether to write OAuth token to file."""
        self.__write_files = value

    @property
    def valid(self):
        """:returns: Whether the token file is currently valid."""
        return self.__valid

    @valid.setter
    def valid(self, value):
        """Set whether the token file is currently valid or not.
        :param value: Whether the token file is currently valid or not."""
        self.__valid = value


class FileChangeListener(FileSystemEventHandler):
    """Listener notifying tokens of changes to the files on disk."""

    # Registered token listeners
    __tokens = {}

    # Whether the class has been initialised or not
    __started = None

    def __init__(self):
        """Initialise the observer for the user's home directory."""
        self.__observer = Observer()
        self.__observer.schedule(self, (expanduser('~')))
        self.__observer.start()

    def __del__(self):
        """Stop the observer thread."""
        self.__observer.stop()

    @classmethod
    def start(cls):
        """Initialise the listener and start the thread."""
        if cls.__started is None:
            cls.__started = FileChangeListener()

    @classmethod
    def add_token(cls, tokenFile, token):
        """Add the specified token as a listener.
        :param type: The type of token to register (dev, QA, production).
        :param token: The token to register."""
        if tokenFile not in cls.__tokens.keys():
            cls.__tokens[tokenFile] = []

        # add a weak reference to the token
        cls.__tokens[tokenFile].append(weakref.ref(token))

    @classmethod
    def remove_token(cls, token):
        """Delete the token from the listener list.
        :param token: The token to remove form the listener lists."""
        for token_list in cls.__tokens.items():
            token_list.remove(token)

    def on_any_event(self, event):
        """React to a token file being changed on disk.
        :param event: The even instance representing the change on disk."""
        for tokenFile in FileChangeListener.__tokens.keys():
            if event.src_path == tokenFile:
                # remove any outdated references
                FileChangeListener.__tokens[tokenFile] = [s for s in FileChangeListener.__tokens[tokenFile] if
                                                          s() is not None]

                # notify any tokens registered for this type
                for token in FileChangeListener.__tokens[tokenFile]:
                    # if the token still exists, mark it as invalid
                    if token() is not None:
                        token().valid = False

    def on_moved(self, event):
        pass

    def on_created(self, event):
        pass

    def on_deleted(self, event):
        pass

    def on_modified(self, event):
        pass


class __ExpiredTokenException(Exception):
    """
        Class used to report an expired token
    """

    def __init__(self):
        self.value = 'Token has expired'

    def __str__(self):
        return repr(self.value)


class __MissingTokenFileException(Exception):
    """
        Class used to report a missing token file
    """

    def __init__(self):
        self.value = 'Token File is Missing'

    def __str__(self):
        return repr(self.value)


def get_token_file_name(postfix):
    """
        Standardised way to get token file name.
        :param type: The TokenServer to get the file name for.
        :returns: The file name for the supplied TokenServer.
    """

    filename = '%s%s%s%s' % (expanduser('~'), os.sep, '.LIGHTPythonClient', postfix)
    return filename


def get_date_string(ts):
    """Format the supplied date as a string.
    :param ts: The date to format as a string.
    :returns: The supplied date formatted as a string."""
    dt = datetime.datetime.fromtimestamp(float(ts))
    return dt.strftime('%A %d %b %Y %H:%M:%S')


@synchronized
def __read_access_token(filename, force=False, logger=None):
    """
        Reads the .LIGHTPythonClient file (if there) and returns the access token.
        If the file is missing it raises a __MissingTokenFileException.
        If the file is there but has expired, raises __ExpiredTokenException
        :param type: The TokenServer to read the cached token for.
        :param force: Whether to ignore the cached token and request a new token.
        :param logger: The logger instance to write to.
        :returns: The read OAuth token.
    """
    token = Token()
    FileChangeListener.add_token(filename, token)

    if force:
        logger.debug('Skipping local file as force is enabled.')
        raise __MissingTokenFileException()

    try:
        logger.debug('Reading token file from %s.' % filename)
        config = EncryptedConfigParser()
        config.read(filename)
        key = client_config.get(section="DEFAULT", option="oauth_secret")

        token.access_token = config.get('OAuth', 'access_token', key)
        token.token_type = config.get('OAuth', 'token_type', key)
        token.expiry_timestamp = float(config.get('OAuth', 'expiry_timestamp', key))
        token.refresh_token = config.get('OAuth', 'refresh_token', key)
        token.write_files = True

        logger.info('Token read successfully, Expires on %s' % get_date_string(token.expiry_timestamp))

        return token
    except IOError:
        raise __MissingTokenFileException()


###################################
#         Azure AD Auth           #
###################################

@synchronized
def __obtain_azure_ad_access_token_with_refresh(token, device_endpoint, token_endpoint, client_id, scope, token_file,
                                                logger):
    """
        Obtain credentials for the user and call PingFederate to get the
        JSON Web Token.
        :param token: The OAuth token to refresh.
        :param type: The TokenServer to request a refresh token from.
        :param logger: The logger instance to write to.
        :returns: The returned OAuth token.
    """

    def fetch_token(azure_ad_token_request_data):
        session = requests.session()
        token_response = session.post(token_endpoint,
                                      params=None,
                                      headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                      data=azure_ad_token_request_data)

        return token_response.json(), token_response.status_code

    token_data = None

    if token:  # Use refresh token to fetch access token

        data, re_code = fetch_token(urllib.parse.urlencode({
            "grant_type": "refresh_token",
            "scope": scope,
            "refresh_token": token.refresh_token,
            "client_id": client_id,
        }))

        if re_code == 200:
            token_data = data

    if not token_data:  # Prompt user to authenticate
        # Record the timestamp just before we call into Ping.
        timestamp = time.time()

        session = requests.Session()
        device_response = session.post(device_endpoint,
                                       params=None,
                                       headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                       data=urllib.parse.urlencode({
                                           "client_id": client_id,
                                           "scope": scope
                                       }))

        if device_response.status_code != 200:
            raise Exception('Device authentication request (%s) is not 200 but %s.' %
                            device_endpoint,
                            device_response.status_code)

        # Get the JSON Web Token Data.
        device_response_data = device_response.json()

        print('Enter code {user_code} at {verification_uri} on a Lilly device to login'.format(
            **device_response_data), file=sys.stderr)

        token_request_data = urllib.parse.urlencode({
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "client_id": client_id,
            "code": device_response_data["device_code"]
        })

        while timestamp + float(device_response_data['expires_in']) > time.time():
            logger.debug("Checking token")
            data, re_code = fetch_token(token_request_data)
            if re_code == 200:
                token_data = data
                break

            if "error" in data and data["error"] == "authorization_pending":
                time.sleep(1)
                continue

            raise Exception("Error processing token response " + str(data))

        if not token_data:
            raise Exception("Device authentication timed out before authentication was completed")

    if not token:
        token = Token()
        FileChangeListener.add_token(token_file, token)
        token.write_files = True

    token.access_token = token_data['access_token']
    token.token_type = token_data['token_type']
    token.refresh_token = token_data['refresh_token']

    # Adjust downwards to make sure we will get an expired token
    # way before we get close to the expiry time that PingFederate has.
    # 10 Minutes will do just fine.
    token.expiry_timestamp = time.time() + float(token_data['expires_in']) - 600

    if token.write_files:
        # Create the new token file.
        config = EncryptedConfigParser()
        config.add_section('OAuth')
        key = client_config.get(section=CONFIG_DEFAULT, option="oauth_secret")

        config.set('OAuth', 'access_token', token.access_token, key)
        config.set('OAuth', 'token_type', token.token_type, key)
        config.set('OAuth', 'expiry_timestamp', str(token.expiry_timestamp), key)
        config.set('OAuth', 'refresh_token', token.refresh_token, key)

        # Write the config file.
        with open(token_file, 'w') as configfile:
            config.write(configfile)

    logger.debug('Token creation successful - expiry on %s' % get_date_string(token.expiry_timestamp))

    return token


@synchronized
def get_azure_ad_access_token(env, token=None, logger=None):
    """
       Returns the OAuth access token using Azure AD device flow

       :param env: The Client to use when retrieving an OAuth token.
       :param token: The current token to refresh if necessary.
       :param logger: The logger instance to write to.
       :returns: The OAuth token returned from Azure AD.
    """

    # set logger
    if logger is None:
        logger = logging
    elif len(logging.Logger.manager.loggerDict) < 1:
        raise Exception("Invalid logger object passed, please create \
            and pass a logger and set to use logging.disable if you don't want logging.")

    # Check the file system listener is initialised
    FileChangeListener.start()

    current_time = time.time()

    token_file = get_token_file_name("AzureAD" + env)

    # if we have no token, or it's invalidated read from disk
    if token is None or not token.valid:
        try:
            token = __read_access_token(token_file, False, logger)
        except Exception as ex:
            logger.debug(ex)

    # Has the token expired ?
    if token and current_time <= token.expiry_timestamp:
        return token

    return __obtain_azure_ad_access_token_with_refresh(token=token,
                                                       client_id=client_config.get(section=env,
                                                                                   option="azure_ad_client_id"),
                                                       scope=client_config.get(section=env,
                                                                               option="azure_ad_scope"),
                                                       token_endpoint=client_config.get(section=CONFIG_DEFAULT,
                                                                                        option="azure_ad_token_endpoint"),
                                                       device_endpoint=client_config.get(section=CONFIG_DEFAULT,
                                                                                         option="azure_ad_device_endpoint"),
                                                       token_file=token_file,
                                                       logger=logger)
