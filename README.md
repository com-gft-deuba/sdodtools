# Intoduction

## When to use this library

This simple library is designed to solve a highly specific problem of my colleagues working with a certain big german bank. It may be usefull for you, if ALL these conditions apply:
- You're working in a SDOD.
- You need to access some APIs, internal or external (i.e. Github or Terraform Enterprise) from your SDOD.
- You want to use python as provided by the SDOD to access the APIs.
- You have to use a proxy with NTLM authentication to access these APIs.
For most other situations, you may want to look for a different/better solution.

The actual problem here is the NTLM authentication of the proxy. The python requests library does not support NTLM authentication out of the box. There're pip packages that add this functionality, but they cannot be installed with the provided python tools ... because pip also needs to access to the packages through the NTLM authentication proxy. 

## How it solves the problem

The solution is very crude. I noticed, that the bash shell that comes with the git installation contains a 'curl' command that supports NTLM authentication to the proxy. So I wrote a subclass of urllibs request.HTTPHandler, that uses the 'curl' command to make the requests, handing off NTLM authentication to the 'curl' cli tool.

## Overview

This library consists of the following packages.

### sdodtools.UrllibCurl

The actual implementation of the HTTPHandler subclass and some helpers. The main class here is 'sdodtools.UrllibCurl.Handler.CurlHandler', a subclass of 'urllib.request.HTTPHandler'. Additionally, the package 'sdodtools.UrllibCurl.Auth' has classes to store credentials for both the APIs and the proxy for use together with the 'CurlHandler'. The 'sdodtools.UrllibCurl.Cli' package contains some helper functions for CLI calls from python.

### sdodtools.Crypt

The 'sdodtools.Crypt' package contains a set of tools to store and retrieve encrypted authentication data. The main class here is 'sdodtools.Crypt.Secrets.Secret'. It is the base class for 'sdodtools.Crypt.Secrets.Login', 'sdodtools.Crypt.Secrets.Cookie', 'sdodtools.Crypt.Secrets.Token', which store the corresponding type of credentials. 

The implementation of the class uses cli calls to the 'openssl' tool. This enables users to use the encrypted data from other shell scripts, by simply calling the 'openssl' tool for decryption.

Encryption keys are managed by the class 'sdodtools.Crypt.Secrets.Key'.

CAREFUL: This class is not designed for security. The purpose is to be compliant with customer demands, that passwords are not stored unecrypted on disk.

Please read the documentation in [Readme_Crypt.md](Readme_Crypt.md) for a more detailed description and examples.

### sdodtools.Cli.Utils

Some helpers for working with CLI commands.

# Examples

## Basic use, no Proxy, no Authentication

    #!/usr/bin/env python3

    import urllib.request
    import sdodtools.UrllibCurl

    # Create the handler
    curl_handler = sdodtools.UrllibCurl.Handler.CurlHandler()

    # Create an opener using the custom handler
    opener = urllib.request.build_opener(curl_handler)

    # Use the opener
    response = opener.open('https://httpbin.org/get')
    print(response.read().decode())

## Use with Proxy, no Authentication, no encryption of secrets

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

## Use with Proxy, Authentication, unencrypted secrets

    #!/usr/bin/env python3

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

## Use with Proxy, Authentication, unencrypted secrets, for multiple servers with different authentication

    #!/usr/bin/env python3

    import urllib.request
    import sdodtools.UrllibCurl
    import sdodtools.Crypt

    api_secret_github   = sdodtools.Crypt.Secrets.Token(header=b'X-Authorization', token=b'mytoken')
    api_login_github = sdodtools.UrllibCurl.Auth.ServerAuth.from_secret(secret=api_secret)
    api_secret_tfe   = sdodtools.Crypt.Secrets.Token(header=b'X-Authorization', token=b'myothertoken')
    api_login_tfe = sdodtools.UrllibCurl.Auth.ServerAuth.from_secret(secret=api_secret)
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

    response = opener_tfe.open('https://httpbin.org/get')
    print(response.read().decode())
