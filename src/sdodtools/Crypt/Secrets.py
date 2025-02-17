import re
import os
import collections

import sys
from .. import Cli

##############################################################################
##############################################################################

class SecretFactory:

    class FormatError(Exception): pass

    RE_FILEPATTERN = re.compile(r'^(?P<domain>[^_.]+)_(?P<name>[^_.]+)\.(?P<category>[^_.]+)')
    KEY_PREFIX = '.secret'
    SecretInfo = collections.namedtuple('SecretInfo', ['basedir', 'prefix', 'domain', 'name', 'category', 'path', 'filename'])
    KeyInfo = collections.namedtuple('KeyInfo', ['basedir', 'prefix', 'path', 'filename'])

    @classmethod
    def from_bytes(cls, b, key=None):

        idx_start = b.find(b'<')

        if idx_start < 0: return None, b

        idx_stop = b.find(b'>', idx_start ) 

        if idx_stop < 0: raise cls.FormatError("Missing '>' in secret class '{b.decode()}'")

        secret_class = b[idx_start+1:idx_stop].decode()

        if secret_class.startswith('__main__.'): secret_class = secret_class[9:]

        if secret_class.find('.') >= 0:

            path = secret_class.split('.')

            try:

                module = __import__('.'.join(path[:-1]), fromlist=[path[-1]])

            except ImportError as e:

                raise cls.FormatError(f"Failed to import module '{path}' at '{path[:-1]}'") from e

            try:

                secret_class = getattr(module, path[-1])

            except AttributeError as e:

                raise cls.FormatError(f"Failed to import class '{path}' at '{path[-1]}'") from e

        else:

            if secret_class not in globals(): raise cls.FormatError(f"Unknown container class '{secret_class}'")

            secret_class = globals()[secret_class]

        return secret_class.from_bytes(b[idx_stop+1:], key=key)

    @classmethod
    def save(cls, secret, overwrite=False, basedir=None, prefix=None) -> str:

        if secret is None: return

        if basedir is None: basedir = secret.basedir

        if basedir is None: basedir = '.'

        if prefix is None: prefix = secret.prefix

        if prefix is None: prefix = cls.KEY_PREFIX

        if isinstance(secret, SecretFactory.KeyInfo):

            filename = os.path.join(basedir, f"{prefix}-key") 

        else:

            filename = os.path.join(basedir, f"{prefix}-{secret.domain}_{secret.name}.{secret.category}") 

        if os.path.exists(filename) and not overwrite: raise Exception(f"File '{filename}' already exists!")

        with open(filename, "wb") as f:

            f.write(bytes(secret))

        return filename

    @classmethod
    def load(cls, fileinfo, key=None):

        if not isinstance(fileinfo, str): fileinfo = fileinfo.path

        with open(fileinfo, "rb") as f:

            content = f.read()
            secret, rest = SecretFactory.from_bytes(content, key=key)

            return secret

    @classmethod
    def find_secrets(cls, basedir=None, prefix=None):

        if basedir is None: basedir = '~/'

        basedir = os.path.expanduser(basedir) 

        if prefix is None: prefix = cls.KEY_PREFIX

        if prefix is None or len(prefix) == 0:

            _prefix = ''

        else:

            _prefix = prefix + '-'

        secret_infos = []
        key_info = None

        for obj in os.listdir(basedir):

            if not obj.startswith(_prefix): continue

            filename = os.path.join(basedir, obj)

            if not os.path.isfile(filename): continue

            fileid = obj[len(_prefix):]

            if fileid == 'key':

                info = cls.KeyInfo(basedir=basedir, prefix=prefix, path=filename, filename=obj)
                key_info = info
                continue

            matches = cls.RE_FILEPATTERN.match(fileid)

            if matches is None: continue

            info = cls.SecretInfo(basedir=basedir, prefix=prefix, domain=matches.group('domain'), name=matches.group('name'), category=matches.group('category'), path=filename, filename=obj)

            secret_infos.append(info)

        return key_info, secret_infos

##############################################################################
##############################################################################

class Container:

    class FormatError(Exception): pass

    @classmethod
    def create_class(cls, class_name):
        base_class_name = cls.__qualname__
        base_module = cls.__module__

        if hasattr(cls, class_name): return getattr(cls, class_name)

        new_class = type(f'{base_class_name}.{class_name}', (cls,), {'_class_signature': f'<{base_module}.{base_class_name}>'})
        new_class.__module__ = base_module
        setattr(cls, class_name, new_class)

        return new_class
        
    @classmethod
    def from_bytes(cls, b, key=None):
        idx_start = b.find(b'[')

        if idx_start < 0: return None, b

        idx_stop = b.find(b']', idx_start ) 

        if idx_stop < 0: raise cls.FormatError("Missing '>' in secret class '{b.decode()}'")

        container = b[idx_start+1:idx_stop]
        secret = b[idx_stop + 1:]

        try:

            domain, name, category = container.split(b"|")

        except ValueError as e:

            raise cls.FormatError(f"Failed to parse container '{container}'") from e

        secret, rest = SecretFactory.from_bytes(secret, key=key)

        cls = cls.create_class(domain.decode())
        return cls(domain=domain.decode(), name=name.decode(), category=category.decode(), secret=secret), rest

    def __init__(self, secret, domain, name, category, *args, **argv) -> None:

        self.secret = secret
        self.domain = domain
        self.name = name
        self.category = category

    def __bytes__(self) -> bytes:

        return f'{self._class_signature}[{self.domain}|{self.name}|{self.category}]'.encode() + bytes(self.secret)

    def _as_clear_bytes(self) -> str:

        return f'{self._class_signature}[{self.domain}|{self.name}|{self.category}]'.encode() + self.secret._as_clear_bytes()

    def __str__(self) -> str:

        return '{sig}[{domain}|{name}|{category}]{secret}'.format(sig=self._class_signature, domain=self.domain, name=self.name,category=self.category,secret=str(self.secret))

    def _as_clear_str(self) -> str:

        return '{sig}[{domain}|{name}|{category}]{secret}'.format(sig=self._class_signature, domain=self.domain, name=self.name,category=self.category,secret=self.secret._as_clear_str())

    def __repr__(self) -> str:

        return f"{self._class_signature}[{self.domain}|{self.name}|{self.category}]" + repr(self.secret)

    def __getattr__(self, name):

        if name == 'key': return self.secret.key

        if name.startswith('clear'):

            basename = name[5:]

        else:

            basename = name

        if basename in self.secret.KEYWORDS:

            return self.secret.__getattr__(name)
        
        return self.self.__dict__[name]

##############################################################################
##############################################################################

class Secret:

    KEYWORDS = []

    class FormatError(Exception): pass

    @classmethod
    def from_bytes(cls, b, key=None):

        idx_start = b.find(b'[')

        if idx_start < 0: return None, b

        idx_stop = b.find(b']', idx_start ) 

        if idx_stop < 0: raise cls.FormatError("Missing '>' in secret class '{b.decode()}'")

        value_list = b[idx_start+1:idx_stop]
        value_list = value_list.split(b"|")
        l_value_list = len(value_list)
        l_keywords = len(cls.KEYWORDS)

        if l_value_list < l_keywords: raise cls.FormatError(f"Missing keywords in secret class. Found {l_value_list} keywords, expected {l_keywords}.")

        if l_value_list > l_keywords: raise cls.FormatError(f"Too many keywords in secret class '{cls.__name__}'. Found {l_value_list} keywords, expected {l_keywords}.")

        values = { keyword: value_list[idx] for idx, keyword in enumerate(cls.KEYWORDS)}

        return cls(key=key, **values), b[idx_stop + 1:]

    @classmethod
    def from_key(cls, key, **argv):

        values = {}

        for keyword in cls.KEYWORDS:

            value = None

            if keyword in argv:

                value = argv[keyword]

                if key is not None:

                    r, value, stderr = key.encrypt(value)
                    r = Cli.Utils.CliException.from_result(message='Failed to encrypt bytes.', r=r, cmd=None, stdout=value, stderr=stderr)

                    if r is not None: raise r

            values[keyword] = value

        secret = cls(key=key, **values)

        if 'domain' in argv and 'name' in argv and 'category' in argv:

            return Container(secret=secret, domain=argv['domain'], name=argv['name'], category=argv['category'])

        return secret

    def __init__(self, key=None, **argv) -> None:

        self.__dict__['key'] = key
        self.__dict__['_class_signature'] =  "<" + ".".join([type(self).__module__, type(self).__qualname__]) + ">" 

        for keyword in self.KEYWORDS:

            if keyword in argv:

                self.__dict__[keyword] = argv[keyword]

            else:

                self.__dict__[keyword] = None

        for arg in argv.keys():

            if arg not in self.KEYWORDS: raise AttributeError(f"Unknown keyword '{arg}'")

    def __getattr__(self, name):

        if name.startswith('clear'):

            is_cleartext = True
            basename = name[5:]

        else:

            is_cleartext = False
            basename = name

        if basename not in self.KEYWORDS:

            if name not in self.__dict__: raise AttributeError(f"'{self.__class__.__qualname__}' object has no attribute '{name}'")

            return self.__dict__[name]
        
        if not is_cleartext: return self.__dict__[name]

        if self.key is None: return self.__dict__[basename]

        if self.__dict__[basename] is None: return None
    
        r, stdout, stderr = self.key.decrypt(self.__dict__[basename])
        r = Cli.Utils.CliException.from_result(message='Failed to encrypt bytes.', r=r, cmd=None, stdout=stdout, stderr=stderr)

        if r is not None: raise r

        return stdout

    def __setattr__(self, name, value):

        if name.startswith('clear'):

            is_cleartext = True
            basename = name[5:]

        else:

            is_cleartext = False
            basename = name

        if basename not in self.KEYWORDS and basename != 'key':

            if name not in self.__dict__: raise AttributeError(f"'{self.__class__.__qualname__}' object has no attribute '{name}'")

            self.__dict__[name] = value
            return 
        
        if not is_cleartext:

            if name == 'key':

                for keyword in self.KEYWORDS:

                    clearkeyword = "clear" + keyword
                    clearattribute = getattr(self, clearkeyword)
                    attribute = clearattribute

                    if value is not None:
                        
                        r, attribute, stderr = value.encrypt(clearattribute)

                        if r != 0: raise Cli.Utils.get_cli_exception(message=f"Failed to encrypt '{keyword}'", r=r, stdout=attribute, stderr=stderr)

                    self.__dict__[keyword] = attribute

            self.__dict__[name] = value
            return 

        if value is None:

            self.__dict__[basename] = value
            return 
        
        r, stdout, stderr = self.key.encrypt(value)

        if r != 0: raise Cli.Utils.get_cli_exception(message=f"Failed to encrypt '{basename}'", r=r, stdout=stdout, stderr=stderr)

        self.__dict__[basename] = stdout
        return

    def __str__(self) -> str:

        values = [getattr(self, x).replace(b'\n', b'').decode() for x in self.KEYWORDS ]
        msg = '|'.join(values)

        return f'{self._class_signature}[{msg}]'

    def __bytes__(self) -> str:

        values = [getattr(self, x) for x in self.KEYWORDS ]
        msg = b'|'.join(values)

        return self._class_signature.encode() + b'[' + msg + b']'

    def _as_clear_str(self) -> str:

        if self.key is not None:
            
            values = [ self.key.decrypt(getattr(self, x))[1].decode() for x in self.KEYWORDS ]

        else:

            values = [getattr(self, x).replace(b'\n', b'').decode() for x in self.KEYWORDS ]

        msg = '|'.join(values)

        return f'{self._class_signature}[{msg}]'

    def _as_clear_bytes(self) -> str:

        if self.key is not None:

            values = [self.key.decrypt(getattr(self, x))[1] for x in self.KEYWORDS ]

        else:

            values = [getattr(self, x) for x in self.KEYWORDS ]

        msg = b'|'.join(values)

        return self._class_signature.encode() + b'[' + msg + b']'

##############################################################################
##############################################################################

class Login(Secret):

    KEYWORDS = ['user', 'password']

##############################################################################
##############################################################################

class Cookie(Secret):

    KEYWORDS = ['header', 'value']

##############################################################################
##############################################################################

class Token(Cookie):

    KEYWORDS = ['header', 'token']
