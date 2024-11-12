# Intoduction

## When to use this library

This is an addition to the UrllibCurl library. It allows you to store and retrieve encrypted secrets on disk. The purpose is to be compliant with customer demands, that passwords are not stored unecrypted on disk. The method is not really secure, since the de/encryption key is stored on disk too. Use this library, when:
- You want to use UrllibCurl.
- You want to store your credentials encrypted on disk in a convenient way.

Without using this library, you'll have to either provide all credentials on the commandline of your scripts or find a completely different way to store and manage your credentials.

## How it solves the problem

The library stores both the de/encryption key and the encrypted secrets on disk. It provides a simple framework to manage the key and the secrets. Encryption and decryption is done using the `openssl` command line tool. This enables users to use the encrypted data from other shell scripts, by simply calling the `openssl` tool for decryption.

# Overview

This library consist of two packages.

## The sdodtools.Crypt.Keys package

The 'sdodtools.Crypt.Keys' package contains a set of tools to manage the encryption key. The main class is `sdodtools.Crypt.Keys.KeyIV`. It is used to generate a new key, store it on disk and retrieve it from disk. The key is used to encrypt and decrypt the secrets. An instance of the KeyIV class can be used to encrypt and decrypt data. Keys can be generated from random numbers or derived from a password.

## The sdodtools.Crypt.Secrets package

The 'sdodtools.Crypt.Secrets' package contains a set of tools to store and retrieve encrypted authentication data. The main class here is 'sdodtools.Crypt.Secrets.Secret'. It is the base class for 'sdodtools.Crypt.Secrets.Login', 'sdodtools.Crypt.Secrets.Cookie', 'sdodtools.Crypt.Secrets.Token', which keep the corresponding type of credentials.

Encryption of the values is only done, when these Secret instances are created with a key. Without a key, data is handled as cleartext.

Additionally, the 'sdodtools.Crypt.Secrets.SecretFactory' class is used to store and load encrypted credentials from disk.

## The crypt_manage commandline tool

This is the frontend for managing your keys and encrypted credentials outside of your scripts.

# Setting up encrypted credentials

To manage the encrypted keys and credentials, we're going to use the crypt_manage commandline tool. This tool is installed with the library. As a first step, collect all the autentication information that you need. For the NTLM proxy, this is usually your windows username and password. For other tools you should create tokens, that are appropriately scoped for their respective task.

## Listing existing credentials

To list all existing credentials, use the following command:
```crypt_manage list```
The output will look like this (assuming you already created some secrets):

    Basedir                   : /home/tsbo
    Prefix                    : .secret
    Keyfile                   : /home/tsbo/.secret-key
    .secret-github_org1.token : <sdodtools.Crypt.Secrets.Token>[lWLoET+lh+hjymgeaJyNaw==|cQm90OC0107YTRIVGh3cfw==]
    .secret-github_org2.token : <sdodtools.Crypt.Secrets.Token>[ulRDMUFi2Qoa9PUzt1sV8w==|rc0Ro0lYaGQxQ2jus6xlsA==]
    .secret-tfe_main.token    : <sdodtools.Crypt.Secrets.Token>[lWLoET+lh+hjymgeaJyNaw==|UIJRM2IrZmxO/6j0ludu4g==]

Using the `--decrypt` option will show the cleartext secrets:

```crypt_manage list --decrypt```

    Basedir                   : /home/tsbo
    Prefix                    : .secret
    Keyfile                   : /home/tsbo/.secret-key
    .secret-github_org1.token : <sdodtools.Crypt.Secrets.Token>[X-Authorization|token for github org org1]
    .secret-github_org2.token : <sdodtools.Crypt.Secrets.Token>[X-Authorization|token for github org org2]
    .secret-tfe_main.token    : <sdodtools.Crypt.Secrets.Token>[X-Authorization|token for tfe]

## Create a key

The first step is to create a key. We generally use one single key for encrypting credentials. This key is stored in the file `~/.secret-key`.
```crypt_manage create key```
This call will generate a key from random numbers. If you want to derive a key from a specific password, use the following syntax:
```crypt_manage create key --password <password>```

## Create a secret

To create secret, use the following syntax:
```crypt_manage create <type> <domain> <name> <keyword> <value>```

The name of the resulting file is derived from these parameters. It will be `~/.secret-<domain>_<name>.<type>`. The value will be encrypted using the key in `~/.secret-key`.

- `<type>` is one of `login`, `cookie`, `token`
- `<domain>` is the general domain, where the secret will be used (i.e. `github`, `tfe`).
- `<name>` is the specific name of the secret. You can use the relevant github org for github secrets.
- `<keyword>` For the `login` type, this is the username. For both the `cookie` and `token` type, this is the name of the header that will be used to send the secret.
- `<value>` This is the actual secret. For the `login` type, this is the password. For the `cookie` and `token` type, this is the token that will be sent in the header.

## Encrypt and decrypt secrets on the CLI

To quickly encrypt a value via the commandline, use the following syntax:
```crypt_manage encrypt <value>```

To quickly decrypt a value via the commandline, use the following syntax:
```crypt_manage decrypt <value>```

## Changing file locations

To change the location and name prefix for the created files, pass the `--basedir` and/or `--prefix` options to the `crypt_manage` command.

```crypt_manage --basedir <targetdir> --prefix <prefix> create <type> <domain> <name> <keyword> <value>```

The name of the resulting file is derived from these parameters. It will be `<basedir>/<prefix>-<domain>_<name>.<type>`.

To use these, he `--basedir` and/or `--prefix` options will need to be passed in all future calls.

# Using the secrets in python scripts

To use the secrets in your python scripts, you need to create an instance of the `sdodtools.Crypt.Secrets.SecretFactory` class. This class will load the key from disk and use it to decrypt the secrets. The following code snippet shows how to use the secrets in your scripts:

    #!/usr/bin/env python3

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

    # Find a secret for a specific use (i.e. the token for gitub org1)
    # Assumes you created the secret with the following command: `crypt_manage create token github org1 X-Authorization mytoken`
    github_org1_token = next((x for x in secret_list if x.domain=='github' and x.name=='org1' and x.category == 'token'), None)
    print(github_org1_token)

    # Build a server authentication token from the secret
    github_org1_server_auth = sdodtools.UrllibCurl.Auth.ServerAuth.from_secret(secret=github_org1_token)
    print(github_org1_server_auth)

    # Find the login for NTLM authentication with the proxy
    # Assumes you created the secret with the following command: `crypt_manage create login proxy main myself mypassword`
    proxy_login = next((x for x in secret_list if x.domain=='proxy' and x.name=='main' and x.category == 'login'), None)
    print(proxy_login)

    # Build a server authentication token from the secret
    proxy_auth = sdodtools.UrllibCurl.Auth.ProxyAuthNTLM.from_secret(secret=proxy_login)
    print(proxy_auth)

To write a key or a secret to disk, just pass it to the `save` method of the `SecretFactory` class:

    sdodtools.Crypt.Secrets.SecretFactory.save(key, basedir=..., prefix=...)
    sdodtools.Crypt.Secrets.SecretFactory.save(secret, basedir=..., prefix=...)



