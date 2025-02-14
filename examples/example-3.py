#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

import urllib.request
import sdodtools.UrllibCurl
import sdodtools.Crypt

api_secret   = sdodtools.Crypt.Secrets.Token(header=b'X-Authorization', token=b'mytoken')
api_login = sdodtools.UrllibCurl.Auth.ServerAuth.from_secret(secret=api_secret)
proxy_secret = sdodtools.Crypt.Secrets.Login(user=b'myself', token=b'mypassword')
proxy_login = sdodtools.UrllibCurl.Auth.ProxyAuthNTLM(secret=proxy_secret)

proxy_maps = sdodtools.UrllibCurl.Proxy.ProxyMaps()
proxy_maps.add('.*', 'myproxy:8080', proxy_login)

# Create the handler
curl_handler = sdodtools.UrllibCurl.Handler.CurlHandler(proxy_maps=proxy_maps, server_auth=api_login)

# Create an opener using the custom handler
opener = urllib.request.build_opener(curl_handler)

# Use the opener
response = opener.open('https://httpbin.org/get')
print(response.read().decode())
