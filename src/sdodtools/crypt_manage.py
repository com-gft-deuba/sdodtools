import sys
import os
import argparse

import sdodtools.Crypt
import sdodtools.Cli.Utils

def main(argv=None):

    if argv is None: argv = sys.argv

    parser = argparse.ArgumentParser(
            prog='crypt_manage',
            description='Secrets managemant tool',
        )
    parser.add_argument('--basedir', type=str, nargs='?', default=os.path.expanduser('~'), help='Base directory for secret files')
    parser.add_argument('--prefix', type=str, nargs='?', default='.secret', help='Prefix for secret filename')
    parser.set_defaults(cmd='list')

    subparsers = parser.add_subparsers(help='Sub-command help')

    subparser = subparsers.add_parser('list', help='List secrets')
    subparser.set_defaults(cmd='list')
    subparser.add_argument('--decrypt', action='store_true', help='Overwrite the file')
    
    subparser_encrypt = subparsers.add_parser('encrypt', help='Create secrets')
    subparser_encrypt.set_defaults(cmd='encrypt')
    subparser_encrypt.add_argument('cleartext', type=str, default=None, help='Domain of the secret')

    subparser_decrypt = subparsers.add_parser('decrypt', help='Create secrets')
    subparser_decrypt.set_defaults(cmd='decrypt')
    subparser_decrypt.add_argument('crypttext', type=str, default=None, help='Domain of the secret')

    subparser_create = subparsers.add_parser('create', help='Create secrets')
    subparsers_create = subparser_create.add_subparsers(help='Sub-command help')

    subparser_create_key = subparsers_create.add_parser('key', help='Create key')
    subparser_create_key.set_defaults(cmd='create')
    subparser_create_key.set_defaults(category='key')
    subparser_create_key.add_argument('--salt', type=str, nargs='?', default=None, help='Salt for the key')
    subparser_create_key.add_argument('--iterations', type=int, nargs='?', default=200000, help='Number of hash iterations')
    subparser_create_key.add_argument('--length', type=int, nargs='?', default=64, help='The key length (multiple of 16)')
    subparser_create_key.add_argument('--password', type=str, nargs='?', default=None, help='The password to hash')

    subparser_create_cookie = subparsers_create.add_parser('cookie', help='Create key')
    subparser_create_cookie.set_defaults(cmd='create')
    subparser_create_cookie.set_defaults(category='cookie')
    subparser_create_cookie.add_argument('--overwrite', action='store_true', help='Overwrite the file')
    subparser_create_cookie.add_argument('domain', type=str, default=None, help='Domain of the secret')
    subparser_create_cookie.add_argument('name', type=str, default=None, help='Name of the secret')
    subparser_create_cookie.add_argument('header', type=str, default=None, help='Header of the cookie')
    subparser_create_cookie.add_argument('value', type=str, default=None, help='Value of the cookie')

    subparser_create_login = subparsers_create.add_parser('login', help='Create key')
    subparser_create_login.set_defaults(cmd='create')
    subparser_create_login.set_defaults(category='login')
    subparser_create_login.add_argument('--overwrite', action='store_true', help='Overwrite the file')
    subparser_create_login.add_argument('domain', type=str, default=None, help='Domain of the secret')
    subparser_create_login.add_argument('name', type=str, default=None, help='Name of the secret')
    subparser_create_login.add_argument('user', type=str, default=None, help='Header of the cookie')
    subparser_create_login.add_argument('password', type=str, default=None, help='Value of the cookie')

    subparser_create_token = subparsers_create.add_parser('token', help='Create key')
    subparser_create_token.set_defaults(cmd='create')
    subparser_create_token.set_defaults(category='token')
    subparser_create_token.add_argument('--overwrite', action='store_true', help='Overwrite the file')
    subparser_create_token.add_argument('domain', type=str, default=None, help='Domain of the secret')
    subparser_create_token.add_argument('name', type=str, default=None, help='Name of the secret')
    subparser_create_token.add_argument('header', type=str, default=None, help='Header of the token')
    subparser_create_token.add_argument('value', type=str, default=None, help='Value of the token')

    args = parser.parse_args(args=argv[1:])
    basedir = args.basedir
    prefix = args.prefix

    if basedir is None or len(basedir) == 0: basedir = '.'

    if prefix is None or len(prefix) == 0: 
        
        prefix = ''
        _prefix = ''

    else:

        _prefix = prefix + '-'

    secret = os.path.join(basedir, '{prefix}key'.format(prefix=_prefix))
    key=None

    if os.path.exists(secret):

        with open(secret, 'rb') as f:

            content = f.read()

            key, rest = sdodtools.Crypt.Keys.KeyIV.from_bytes(content)

    if args.cmd == 'create':

        if args.category == 'key':

            infos = []
            secret = None

            for obj in os.listdir(basedir):

                filename = os.path.join(basedir, obj)

                if not os.path.isfile(filename): continue

                if obj == '{prefix}key'.format(prefix=_prefix): 

                    secret = filename
                    break

            if secret is not None:

                raise(Exception('Secret file already exists at {secret}'.format(secret=secret)))

            secret = os.path.join(basedir, '{prefix}key'.format(prefix=_prefix))

            if args.password is not None and len(args.password) > 0:

                key = sdodtools.Crypt.Keys.KeyIV.from_password( salt=args.salt, count=args.iterations, key_length=args.length, iv_length=args.int(args.length/2), password=args.password)

            else:

                key = sdodtools.Crypt.Keys.KeyIV.generate( salt=args.salt, count=args.iterations, key_length=args.length, iv_length=int(args.length/2))

            with open(secret, 'wb') as f:

                f.write(bytes(key))

            sys.exit(0)

    if args.cmd == 'list':

        secret_list = sdodtools.Crypt.Secrets.SecretFactory.find_secrets(
                basedir=args.basedir,
                prefix=args.prefix
            )
        secret_list.sort(key=lambda x: (x.domain, x.name, x.category))
        max_len_filename = 0

        for secret_info in secret_list:

            l = len(secret_info.filename)

            if l > max_len_filename: max_len_filename = l

        print('{title:<{title_len}} : {text}'.format(
            title='Basedir',
            title_len=max_len_filename,
            text=basedir))
        print('{title:<{title_len}} : {text}'.format(
            title='Prefix',
            title_len=max_len_filename,
            text=prefix))
        print('{title:<{title_len}} : {text}'.format(
            title='Keyfile',
            title_len=max_len_filename,
            text=secret))

        for secret_info in secret_list:

            container = None

            try:

                container = sdodtools.Crypt.Secrets.SecretFactory.load(filename=secret_info.path, key=key)

            except: pass

            if container is None:

                secret = "FAILED TO LOAD '{filename}'!".format(filename=secret_info.path)

            else:

                if isinstance(container, sdodtools.Crypt.Secrets.Container):

                    secret = container.secret

                else:

                    secret = container

            if 'decrypt' in args and args.decrypt:

                try:

                    text = secret._as_clear_str()

                except: 

                    text = "FAILED TO DECRYPT '{filename}'!".format(filename=secret_info.path)

            else:

                text = str(secret)

            print('{title:<{title_len}} : {text}'.format(
                title=secret_info.filename,
                title_len=max_len_filename,
                text=text
            ))

        sys.exit(0)

    if key is None:

        raise(Exception('Secret {secret} not found!'.format(secret=secret)))

    if args.cmd == 'decrypt':

        crypttext = args.crypttext

        if crypttext is None: crypttext = ''

        crypttext = crypttext.encode()

        status, stdout, stderr = key.decrypt(crypttext)

        if status == 0:

            print(stdout)
            sys.exit(10)

        r = sdodtools.Cli.Utils.CliException.from_result(message='Failed to decrypt bytes.', r=status, cmd=None, stdout=stdout, stderr=stderr)

        raise r

    if args.cmd == 'encrypt':

        cleartext = args.cleartext

        if cleartext is None: cleartext = ''

        cleartext = cleartext.encode()
        status, stdout, stderr = key.encrypt(cleartext)

        if status == 0:

            print(stdout)
            sys.exit(10)

        r = sdodtools.Cli.Utils.CliException.from_result(message='Failed to encrypt bytes.', r=status, cmd=None, stdout=stdout, stderr=stderr)

        raise r

    if args.cmd == 'create':

        if args.category == 'cookie':

            header = args.header.encode()
            value = args.value.encode()
            cookie = sdodtools.Crypt.Secrets.Cookie.from_key(key=key, domain=args.domain, name=args.name, category='cookie', header=header, value=value) 
            print(cookie)
            filename = sdodtools.Crypt.Secrets.SecretFactory.save(secret=cookie, basedir=basedir, prefix=prefix)  
            print('Cookie saved to {filename}'.format(filename=filename))
            sys.exit(0)

        if args.category == 'login':

            user = args.user.encode()
            password = args.password.encode()
            login = sdodtools.Crypt.Secrets.Login.from_key(key=key, domain=args.domain, name=args.name, category='login', user=user, password=password) 
            print(login)
            filename = sdodtools.Crypt.Secrets.SecretFactory.save(secret=login, basedir=basedir, prefix=prefix)  
            print('Login saved to {filename}'.format(filename=filename))
            sys.exit(0)

        if args.category == 'token':

            header = args.header.encode()
            value = args.value.encode()
            token = sdodtools.Crypt.Secrets.Token.from_key(key=key, domain=args.domain, name=args.name, category='token', header=header, value=value) 
            print(token)
            filename = sdodtools.Crypt.Secrets.SecretFactory.save(secret=token, basedir=basedir, prefix=prefix, overwrite=args.overwrite)  
            print('Token saved to {filename}'.format(filename=filename))
            sys.exit(0)

    sys.exit(1)

if __name__ == '__main__':

    main(sys.argv)
