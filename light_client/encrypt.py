#!/usr/bin/env python
"""
    This module contains utilities for encrypting and decrypting configuration files.

    Note that the algorithm uses the machine MAC, so anything encrypted has to be decrypted on the same computer
"""


import hashlib
import os.path
import sys
import uuid

from base64 import b64encode, b64decode
from configparser import ConfigParser
from Crypto import Random
from Crypto.Cipher import AES


class EncryptedConfigParser(ConfigParser):
    """Class to encrypt a configuration file using AES.
    Adapted from http://stackoverflow.com/questions/16761458/how-to-aes-encrypt-decrypt-files-using-python-pycrypto-in-an-openssl-compatible
    """

    # the character encoding to use for strings to bytes
    __encoding = 'utf-8'

    # the header for the salt in the output string
    __salt_header = 'salthdr'

    # the length the key will be pad/truncated to
    __key_length = 32

    # the length of the initialisation vector
    __iv_length = AES.block_size
    
    class __GetSuperFix(object):
        """Class to fix issue with Python3+ ConfigParser where it will cause a stack overflow
        by calling EncryptedConfigParser's get method, from ConfigParser's get method.
        This is achieved by replacing the get method in EncryptedConfigParser with the one
        for ConfigParser temporarily while it calls the super method."""

        def __enter__(self):
            """Override the get method of the EncryptedConfigParser."""
            self.__backup = EncryptedConfigParser.get
            EncryptedConfigParser.get = ConfigParser.get
        
        def __exit__(self, type, value, traceback):
            """Restore the original get method of the EncryptedConfigParser."""
            EncryptedConfigParser.get = self.__backup
    
    def __init__(self, ):
        ConfigParser.__init__(self)

    def get(self, section, option, key=None):
        """Override parent get method to decrypt the stored value.
        :param section: The config section to retrieve.
        :param option: The config option to retrieve.
        :param key: The decryption key to use, if None a key will be generated.
        :return: The decrypted value for the given section and option."""
        with self.__GetSuperFix():
            value = ConfigParser.get(self, section, option)
        return self.__decrypt(value, key=key)

    def set(self, section, option, value, key=None):
        """Override parent set method to encrypt the stored value.
        :param section: The config section to store.
        :param option: The config option to store.
        :param key: The encryption key to use, if None a key will be generated.
        :param value: The unencrypted config value to store."""
        value = str(self.__encrypt(value, key=key))
        return ConfigParser.set(self, section, option, value)

    @classmethod
    def __derive_key(cls, salt):
        key = bytes('', cls.__encoding)
        temp = bytes('', cls.__encoding)
        uid = bytes('%s' % uuid.getnode(), cls.__encoding)
        if not isinstance(salt, bytes):
            salt = bytes(salt, cls.__encoding)
        while len(key) < cls.__key_length + cls.__iv_length:
            temp += uid
            temp += salt
            temp = hashlib.md5(temp).digest()
            key += temp

        return key[:cls.__key_length], key[cls.__key_length:cls.__key_length + cls.__iv_length]

    @classmethod
    def __encode_key(cls, key, salt):
        if not isinstance(key, bytes):
            key = bytes(key, cls.__encoding)
        if not isinstance(salt, bytes):
            salt = bytes(salt, cls.__encoding)

        encoded = key + salt
        while len(encoded) < cls.__key_length + cls.__iv_length:
            encoded += b'.'

        return encoded[:cls.__key_length], encoded[cls.__key_length:cls.__key_length + cls.__iv_length]

    @classmethod
    def __encrypt(cls, in_str, key=None):
        """Encrypt the given clear text.
        :param in_str: The clear text to encrypt.
        :param key: The encryption key to use, if None a key will be generated.
        :return: The encrypted string.
        """
        # calculate a salt
        salt = Random.new().read(AES.block_size)
        salt = salt[:(AES.block_size - len(cls.__salt_header))]

        # retrieve/create the key
        if key is None:
            key, iv = cls.__derive_key(salt)
        else:
            key, iv = cls.__encode_key(key, salt)

        # create the cipher
        cipher = AES.new(key, AES.MODE_CFB, iv)

        # encrypt
        clear_text = in_str
        if not isinstance(clear_text, bytes):
            clear_text = bytes(clear_text, cls.__encoding)
        encrypted = cipher.encrypt(clear_text)

        # include salt
        salted = bytes(cls.__salt_header, cls.__encoding) + salt + encrypted

        # encode
        encoded = b64encode(salted)
        if isinstance(encoded, bytes):
            encoded = encoded.decode(cls.__encoding)

        return encoded

    @classmethod
    def __decrypt(cls, in_str, key=None):
        """Decrypt the given cipher text.
        :param in_str: The cipher text to decrypt.
        :param key: The decryption key to use, if None a key will be generated.
        :return: The decrypted string.
        """
        # decode the value
        decoded = b64decode(in_str)

        # extract the salt
        salt = decoded[len(cls.__salt_header):AES.block_size]
        desalted = decoded[AES.block_size:]

        # retrieve/create the key
        if key is None:
            key, iv = cls.__derive_key(salt)
        else:
            key, iv = cls.__encode_key(key, salt)

        # create the cipher
        cipher = AES.new(key, AES.MODE_CFB, iv)

        # decrypt
        decrypted = cipher.decrypt(desalted)
        if isinstance(decrypted, bytes):
            decrypted = decrypted.decode(cls.__encoding)

        return decrypted

    @classmethod
    def encrypt_config_file(cls, in_config_file, out_config_file, key=None):
        """ Encrypt the given config file values and save to file.
        :param in_config_file The input config file to encrypt the values of.
        :param out_config_file The output config file to write the encrypted values to.
        :param key: The encryption key to use, if None a key will be generated.
        """
        in_config = ConfigParser()
        in_config.read(in_config_file)

        # Create a new config file with encrypted values
        out_config = ConfigParser()
        for section in in_config.sections():
            out_config.add_section(section)
            for option in in_config.options(section):
                out_config.set(section, option, cls.__encrypt(in_config.get(section, option), key=key))

        # Write the new config file
        out_file = open(out_config_file, 'w')
        out_config.write(out_file)
        out_file.close()

    @classmethod
    def decrypt_config_file(cls, config_file, key=None):
        """ Decrypt the given config file and return the unencrypted config.
        :param config_file The input config file to decrypt.
        :param key: The encryption key to use, if None a key will be generated.
        :return The unencrypted config object.
        """
        in_config = ConfigParser()
        in_config.read(config_file)

        # Decrypt the config file values
        for section in in_config.sections():
            for option in in_config.options(section):
                in_config.set(section, option, cls.__decrypt(in_config.get(section, option), key=key))
        return in_config


def main():
    """Main provides encryption of specified config file."""
    if len(sys.argv) < 3:
        print('Application expects input config file and output config file on command line.')
        print('e.g. %s inFile.ini outFile.ini' % sys.argv[0])
        return

    if not os.path.isfile(sys.argv[1]):
        print('Input file %s does not exist.' % sys.argv[1])
        return

    # read the input config file
    c = ConfigParser()
    c.read(sys.argv[1])

    # copy the keys to the encrypted parser
    e = EncryptedConfigParser()
    for section in c.sections():
        e.add_section(section)
        for option in c.options(section):
            e.set(section, option, c.get(section, option))

    # write the encrypted parser
    with open(sys.argv[2], 'w') as out_file:
        e.write(out_file)
    print('Input config file %s has been encrypted as %s.' % (sys.argv[1], sys.argv[2]))


if __name__ == '__main__':
    main()
