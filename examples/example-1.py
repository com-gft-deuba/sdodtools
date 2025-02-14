#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

import urllib.request
import sdodtools.UrllibCurl

# Create the handler
curl_handler = sdodtools.UrllibCurl.Handler.CurlHandler()

# Create an opener using the custom handler
opener = urllib.request.build_opener(curl_handler)

opener.add_handler(urllib.request.ProxyHandler({}))
# Use the opener
response = opener.open('https://httpbin.org/get')
print(response.read().decode())
