#!/usr/bin/env python
"""
    LIGHT Client
"""

import datetime
import getpass
import logging
import os
import requests
import sys
import time
import logging

from .encrypt import EncryptedConfigParser
from .oauth_login import get_azure_ad_access_token
from ._version import __version__
from configparser import ConfigParser

AUTH_METHOD_AZURE_AD="azure_ad"
AUTH_METHOD_AWS="aws"
DOTAWS_FILEPATH = os.path.expanduser("~/.aws")
DOTAWS_CONFIG_FILEPATH = DOTAWS_FILEPATH + "/config"
DOTAWS_CREDENTIALS_FILEPATH = DOTAWS_FILEPATH + "/credentials"
ENV_DEV = "DEV"
ENV_QA = "QA"
ENV_PRD = "PRD"

class LIGHTClient():
    """Class to support API calls to LIGHT hosted apps."""

    __S3_AUTH_URLS = {
        ENV_DEV: "https://cloud-browser.apps-api-d.lrl.lilly.com",
        ENV_QA: "https://cloud-browser.apps-api-q.lrl.lilly.com",
        ENV_PRD: "https://cloud-browser.apps-api.lrl.lilly.com"
    }
    

    def __init__(self, auth_method=AUTH_METHOD_AZURE_AD, env=ENV_PRD):
        """Construct a new web service client with the supplied URL base.
        
        :param auth_method Authentication Method
        """
        self.env = env
        self.__s3_auth_url = self.__S3_AUTH_URLS[self.env]
        if auth_method == AUTH_METHOD_AZURE_AD:
            self.get_auth_header = self.__add_azure_ad_auth
        elif auth_method == AUTH_METHOD_AWS:
            self.get_auth_header = self.get_aws_header
        else:
            raise NotImplemented(f"Auth method {auth_method} not implemented")

        # set up for OAuth
        self.__token_cache = None

        self.headers = {'User-Agent': 'light_client.py/%s (%s)' % (__version__, sys.platform)}

    def get_aws_header(self, **kwargs):
        auth_headers = ["Authorization", "X-Amz-Security-Token", "X-Amz-Date"]
        # Importing here so we retain a small dependency footprint for minimal case.
        from boto3 import Session
        from botocore.awsrequest import AWSRequest
        from botocore.compat import HTTPHeaders
        from botocore.hooks import HierarchicalEmitter
        from botocore.model import ServiceId
        from botocore.signers import RequestSigner
        session = Session(**kwargs)
        credentials = session.get_credentials()
        emitter = HierarchicalEmitter()
        signer = RequestSigner(ServiceId("STS"), 'us-east-1', "sts", "v4", credentials, emitter)
    
        url = "https://sts.amazonaws.com/"
    
        headers = HTTPHeaders()
        headers.add_header("Content-Type", "application/x-www-form-urlencoded; charset=utf-8")
        request = AWSRequest("POST", url, headers,
                             data="Action=GetCallerIdentity&Version=2011-06-15", params={})
        signer.sign("GetCallerIdentity", request)
        return {h:k for h, k in request.headers.items() if h in auth_headers}


    def __set_headers(self, params):
        headers = {**self.headers, 
                    **self.get_auth_header()}

        if "headers" in params:
            params["headers"] = {**headers, 
                                 **params["headers"]}
        else:
            params["headers"] = headers

    
    def __clean_params(self, params, accepted_params: [str]):
        """
        Prepare params to be sent to various credential provider APIs
        """
        _params = {}
        for key, value in params.items():
            if key in accepted_params:
                _params[key] = value.lower() if type(value) == str else value
        return _params
    

    #change f string to keyword args
    def get_aws_creds(self, **kwargs):
        """
        Retrieve credentials from the S3 Cloud Browser Auth Server
        """
        accepted_params = [
            "bucket",
            "namespace",
            "prefix",
            "profile",
            "service",
        ]
        params = self.__clean_params(kwargs, accepted_params)
        if kwargs['service'] == 's3':
            url = self.__s3_auth_url + "/auth"
            resp = self.get(url, params=params)
            if resp.status_code != 200:
                raise Exception(f"error requesting AWS creds from ({self.__s3_auth_url}), status code {resp.status_code}")
            
            creds = resp.json()
            credentials_options = {
                'aws_access_key_id': creds['AccessKeyId'],
                'aws_secret_access_key': creds['SecretAccessKey'],
                'aws_session_token': creds['SessionToken'],
                'note': f"expires at {creds['Expiration']}",
            }
            self.write_dotaws_file(filepath=DOTAWS_CREDENTIALS_FILEPATH, header=params['profile'], options=credentials_options)
            return creds
        
        else:
            raise Exception(f"service other than s3 was specified...")


    def aws_cred_refresh(self):
        """
        Refresh S3 credentials from the S3 Cloud Browser Auth Server
        """
        return self.get_aws_creds()
    

    def get_namespaces(self):
        """
        Retrieve all available namespaces with permissions via the S3 Cloud Browser Auth Server
        """
        url = self.__s3_auth_url + "/namespaces"
        resp = self.get(url)
        if resp.status_code != 200:
            raise Exception(f"error requesting namespaces from ({url}), status code {resp.status_code}")
        data = resp.json()
        return data
    

    def get_buckets(self, **kwargs):
        """
        Retrieve all available buckets with permissions via the S3 Cloud Browser Auth Server

        namespace: str constrain credentials to permissions within target namespace
        """
        accepted_params = [
            "namespace",
        ]
        params = self.__clean_params(kwargs, accepted_params)
        url = self.__s3_auth_url + "/buckets"
        resp = self.get(url, params=params)
        if resp.status_code != 200:
            raise Exception(f"error requesting buckets from ({url}), status code {resp.status_code}")
        data = resp.json()
        return data
    

    def get_prefixes(self, **kwargs):
        """
        Retrieve all available buckets with permissions via the S3 Cloud Browser Auth Server

        namespace: str constrain credentials to permissions within target namespace
        bucket: str constrain credentials to permissions with target bucket
        """
        accepted_params = [
            "namespace",
            "bucket",
        ]
        params = self.__clean_params(kwargs, accepted_params)
        url = self.__s3_auth_url + "/prefixes"
        resp = self.get(url, params=params)
        if resp.status_code != 200:
            raise Exception(f"error requesting prefixes from ({url}), status code {resp.status_code}")
        data = resp.json()
        return data
    

    def update_dotaws_config_section(self, **kwargs):
        """
        Returns profile config with new s3 command

        namespace: str constrain credentials to permissions within target namespace
        bucket: str constrain credentials to permissions with target bucket
        prefix: str constrain credentials to permissions with target prefix
        profile: str name of the profile in ~/.aws/config
        service: str AWS service related to config update
        """
        accepted_params = [
            "service",
            "namespace",
            "bucket",
            "prefix",
            "profile",
        ]
        params = self.__clean_params(kwargs, accepted_params)
        header = f"profile {params.pop('profile')}"
        config_section_options = {}
        
        if params["service"] == "s3":
            credential_command = "light_auth creds"
            for param_name, param_value in params.items():
                if param_value:
                    credential_command += f" --{param_name}={param_value}"
            config_section_options = {
                's3_command': credential_command
            }
        
        return self.write_dotaws_file(filepath=DOTAWS_CONFIG_FILEPATH, header=header, options=config_section_options)


    def write_dotaws_file(self, filepath: str, header: str, options: dict):
        """
        Write or update profile block in ~/.aws/config or ~/.aws/credentials

        header: str name of the header of the target section in ~/.aws/config ~/.aws/credentials
        options: dict of config options to write to profile section
        """

        if not os.path.exists(filepath):
            os.makedirs(DOTAWS_FILEPATH, exist_ok=True)
        
        try:
            configs = ConfigParser()
            with open(filepath, 'r') as stream:
                configs.read_file(stream, source=filepath)
            
            if header not in configs.sections():
                configs.add_section(header)
            configs._sections[header].update(options)
            with open(filepath, "w", encoding="utf-8") as f:
                configs.write(f)

        except Exception as e:
            raise Exception(f"error writing {filepath}, {e}")
        

    def get(self, *args, **kwargs):
        """Perform a GET request
        Wrapper around requests.get
        
        :return Requests response
        """
        self.__set_headers(kwargs)

        return requests.get(*args, **kwargs)


    def head(self, *args, **kwargs):
        """Perform a HEAD request
        Wrapper around requests.head
        
        :return Requests response
        """
        self.__set_headers(kwargs)

        return requests.head(*args, **kwargs)


    def post(self, *args, **kwargs):
        """Perform a POST request
        Wrapper around requests.post
        
        :return Requests response
        """
        self.__set_headers(kwargs)

        return requests.post(*args, **kwargs)


    def put(self, *args, **kwargs):
        """Perform a PUT request
        Wrapper around requests.put
        
        :return Requests response
        """
        self.__set_headers(kwargs)

        return requests.put(*args, **kwargs)


    def delete(self, *args, **kwargs):
        """Perform a DELETE request
        Wrapper around requests.delete
        
        :return Requests response
        """
        self.__set_headers(kwargs)

        return requests.delete(*args, **kwargs)


    def options(self, *args, **kwargs):
        """Perform a OPTIONS request
        Wrapper around requests.options
        
        :return Requests response
        """
        self.__set_headers(kwargs)

        return requests.options(*args, **kwargs)


    def patch(self, *args, **kwargs):
        """Perform a PATCH request
        Wrapper around requests.patch
        
        :return Requests response
        """
        self.__set_headers(kwargs)

        return requests.patch(*args, **kwargs)


    def __add_azure_ad_auth(self):
        self.__token_cache = get_azure_ad_access_token(self.env, 
                                                       token=self.__token_cache,
                                                       logger=logging)
        return {"Authorization": self.__token_cache.auth_header}
