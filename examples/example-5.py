#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

import sdodtools.UrllibCurl
import sdodtools.Crypt

# The find_secrets function returns the information about the key and all secrets to a given basedir and prefix.
# When you don't pass basedir or prefix, the default values are used.
key_info, secret_infos = sdodtools.Crypt.Secrets.SecretFactory.find_secrets()

# First load the key from disk, it's needed for the secrets
key = sdodtools.Crypt.Secrets.SecretFactory.load(key_info)

secret_list = []

# Load all the found secrets
for secret in secret_infos:

    secret_list.append(sdodtools.Crypt.Secrets.SecretFactory.load(secret, key=key))

for secret in secret_list:

    print(f"Found the following secret: {str(secret)}.")

# Find a secret for a specific use (i.e. the secret for gitub org1)
# secret_github_org1 = [x for x in secret_list if x.domain=='aaa' and x.name=='bbb' and x.categroy=='cookie']
token_github_org1 = next((x for x in secret_list if x.domain=='github' and x.name=='org1' and x.category == 'token'), None)
token_github_org1 = next((x for x in secret_list if x.domain=='ddd' and x.name=='eee' and x.category == 'token'), None)
print(token_github_org1)

# Build a server authentication token from the secret
server_auth_github_org1 = sdodtools.UrllibCurl.Auth.ServerAuth.from_secret(secret=token_github_org1)
print(server_auth_github_org1)

# Build a server authentication token from the secret
proxy_auth = sdodtools.UrllibCurl.Auth.ProxyAuthNTLM.from_secret(secret=token_github_org1)
print(proxy_auth)