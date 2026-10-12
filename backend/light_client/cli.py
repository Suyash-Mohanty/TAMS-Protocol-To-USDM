"""
light_auth
"""
import argparse
import json
from .oauth_login import get_azure_ad_access_token, get_token_file_name
from .client import LIGHTClient
import os

parser = argparse.ArgumentParser(
    "light_auth", 
    description="Prints authentication token for light hosted applications", 
    usage="light_auth [-h] [-e {DEV,QA,PRD}] [-H] [option]",
    formatter_class=argparse.RawTextHelpFormatter
)

# TODO Modernize API implemention LIST/SHOW/GET/DESCRIBE etc.
parser.add_argument(
    'option',
    default="token", 
    help="""
refresh-login   wipe existing tokens & re-fetch tokens to ensure interactive authentication prompt will not be displayed in subsequent commands
token           get token (default)
namespaces      returns list of namespaces allowed based on scoped s3-credentials
buckets         returns list of buckets allowed based on scoped s3-credentials
prefixes        returns list of prefixes allowed based on scoped s3-credentials
creds           return access tokens that allow scoped access to s3. Can also pass {bucket, namespace in that order} get more specificly scoped credentials. This can be used in an AWS profile as a credential provider
setup           setup AWS profile in ~/.aws/config to use light_auth as a credential provider
""",
    nargs="?"
)

parser.add_argument(
    '-e', '--env', 
    choices=["DEV","QA","PRD"], 
    default="PRD", 
    help="authentication environment (default=PRD)"
)

parser.add_argument(
    "-H","--header",
    help="return the full header",
    action="store_true"
)

parser.add_argument(
    '-p', '--profile', '--profile_name',
    default='lilly-cloud',
    help="supply a profile name to create a named profile",
    nargs='?'
)

parser.add_argument(
    '-b', '--bucket',
    help="supply an s3 bucket name",
    nargs='?'
)

parser.add_argument(
    '-n', '--namespace',
    help="supply a kubernetes namespace name",
    nargs='?'
)

parser.add_argument(
    '-P', '--prefix',
    help="supply an s3 key prefix",
    nargs='?'
)

parser.add_argument(
    '-s', '--service',
    help="supply an AWS service (currently only S3 is supported)",
    default="s3",
    nargs='?'
)

def main():
    args = parser.parse_args()
    kwargs = {}
    for arg in args._get_kwargs():
        kwargs[arg[0]] = arg[1]
    env = args.env.upper()
    subcommand = args.option.lower()

    if subcommand=="refresh-login":
        fname = get_token_file_name("AzureAD" + env)
        os.unlink(fname)
    token = get_azure_ad_access_token(env)

    if subcommand=="token":
        if args.header:
            print(f"Authorization: {token.auth_header}")
            return
        else:
            print(token.access_token)
            return
        
    if subcommand=="namespaces":
        print(json.dumps(LIGHTClient(env=env).get_namespaces()))
        return
    
    if subcommand=="buckets":
        print(json.dumps(LIGHTClient(env=env).get_buckets(**kwargs)))
        return
    
    if subcommand=="prefixes":
        print(json.dumps(LIGHTClient(env=env).get_prefixes(**kwargs)))
        return
    
    if subcommand=="creds":
        print(json.dumps(LIGHTClient(env=env).get_aws_creds(**kwargs)))
        return

    if subcommand=="setup":
        LIGHTClient(env=env).update_dotaws_config_section(**kwargs)
        LIGHTClient(env=env).get_aws_creds(**kwargs)
        return

    print(f"unknown command {subcommand}")
    exit(1)

if __name__ == "__main__":
    main()
