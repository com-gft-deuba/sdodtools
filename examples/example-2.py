#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

import urllib.request
import sdodtools.UrllibCurl

proxy_maps = sdodtools.UrllibCurl.Proxy.ProxyMaps()
proxy_maps.add('.*', 'myproxy:8080')

# Create the handler
curl_handler = sdodtools.UrllibCurl.Handler.CurlHandler(proxy_maps=proxy_maps)

# Create an opener using the custom handler
opener = urllib.request.build_opener(curl_handler)

# Use the opener
response = opener.open('https://httpbin.org/get')
print(response.read().decode())
