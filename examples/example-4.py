#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

import urllib.request
import sdodtools.UrllibCurl
import sdodtools.Crypt

api_secret_github   = sdodtools.Crypt.Secrets.Token(header=b'X-Authorization', token=b'mytoken')
api_login_github = sdodtools.UrllibCurl.Auth.ServerAuth.from_secret(secret=api_secret_github)
api_secret_tfe   = sdodtools.Crypt.Secrets.Token(header=b'X-Authorization', token=b'myothertoken')
api_login_tfe = sdodtools.UrllibCurl.Auth.ServerAuth.from_secret(secret=api_secret_tfe)
proxy_secret = sdodtools.Crypt.Secrets.Login(user=b'myself', token=b'mypassword')
proxy_login = sdodtools.UrllibCurl.Auth.ProxyAuthNTLM(secret=proxy_secret)

proxy_maps = sdodtools.UrllibCurl.Proxy.ProxyMaps()
proxy_maps.add('.*', 'myproxy:8080', proxy_login)

# Create the handlers
curl_handler_github = sdodtools.UrllibCurl.Handler.CurlHandler(proxy_maps=proxy_maps, server_auth=api_login_github)
curl_handler_tfe = sdodtools.UrllibCurl.Handler.CurlHandler(proxy_maps=proxy_maps, server_auth=api_login_tfe)

# Create openers using the custom handler
opener_github = urllib.request.build_opener(curl_handler_github)
opener_tfe = urllib.request.build_opener(curl_handler_tfe)

# Use the opener
response = opener_github.open('https://httpbin.org/get')
print(response.read().decode())


# Show the actual used curl command
import pipes
req = urllib.request.Request('https://httpbin.org/get')
curl_cmd = curl_handler_github._build_curl_command(req, 'https', obfuscate=True)
curl_cmd = [ pipes.quote(x) for x in curl_cmd ]
curl_cmd = ' '.join(curl_cmd)
print(curl_cmd)
