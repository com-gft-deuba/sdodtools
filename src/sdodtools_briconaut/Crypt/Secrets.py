import re
import os
import collections
import Cli.Utils

##############################################################################
##############################################################################

class SecretFactory:

    RE_FILEPATTERN = re.compile(r'^(?P<domain>[^_.]+)_(?P<name>[^_.]+)\.(?P<category>[^_.]+)')
    KEY_PREFIX = '.secret'
    FileInfo = collections.namedtuple('FileInfo', ['domain', 'name', 'category', 'path', 'filename'])

    @classmethod
    def from_bytes(cls, b, key=None):

        idx_start = b.find(b'<')

        if idx_start < 0: return None, b

        idx_stop = b.find(b'>', idx_start ) 
        secret_class = b[idx_start+1:idx_stop].decode()

        if secret_class.startswith('__main__.'): secret_class = secret_class[9:]

        if secret_class.find('.') >= 0:

            path = secret_class.split('.')
            module = __import__('.'.join(path[:-1]), fromlist=[path[-1]])
            secret_class = getattr(module, path[-1])

        else:

            secret_class = globals()[secret_class]

        return secret_class.from_bytes(b[idx_start:], key=key)

    @classmethod
    def save(cls, secret, overwrite=False, basedir=None, prefix=None) -> str:

        if secret is None: return

        if basedir is None: basedir = '.'

        if prefix is None: prefix = cls.KEY_PREFIX

        filename = os.path.join(basedir, f"{prefix}-{secret.domain}_{secret.name}.{secret.category}") 

        if os.path.exists(filename) and not overwrite: raise Exception(f"File '{filename}' already exists!")

        with open(filename, "wb") as f:

            f.write(bytes(secret))

        return filename

    @classmethod
    def load(cls, filename, key=None):

        if not isinstance(filename, str): filename = filename.path

        with open(filename, "rb") as f:

            content = f.read()
            secret, rest = SecretFactory.from_bytes(content, key=key)

            return secret

    @classmethod
    def find_secrets(cls, basedir=None, prefix=None):

        if basedir is None: basedir = '.'

        if prefix is None: prefix = cls.KEY_PREFIX

        if prefix is None:

            _prefix = ''

        else:

            _prefix = prefix + '-'

        infos = []

        for obj in os.listdir(basedir):

            if not obj.startswith(_prefix): continue

            filename = os.path.join(basedir, obj)

            if not os.path.isfile(filename): continue

            fileid = obj[len(_prefix):]

            matches = cls.RE_FILEPATTERN.match(fileid)

            if matches is None: continue

            info = cls.FileInfo(domain=matches.group('domain'), name=matches.group('name'), category=matches.group('category'), path=filename, filename=obj)

            infos.append(info)

        return infos

##############################################################################
##############################################################################

class Container:

    @classmethod
    def from_bytes(cls, b, key=None):

        if not b.startswith(b'['):

            idx_start = b.find(b'[')
            b = b[idx_start + 1:]

        idx_stop = b.find(b']') 
        domain, name, category = b[:idx_stop].split(b"|")
        secret, rest = SecretFactory.from_bytes(b[idx_stop + 1:], key=key)

        return cls(domain=domain.decode(), name=name.decode(), category=category.decode(), secret=secret), rest

    def __init__(self, secret, domain, name, category, *args, **argv) -> None:

        self.secret = secret
        self.domain = domain
        self.name = name
        self.category = category
        self._class_signature = "<" + ".".join([type(self).__module__, type(self).__qualname__]) + ">"

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

    @classmethod
    def from_bytes(cls, b, key=None):

        if not b.startswith(b'['):

            idx_start = b.find(b'[')
            b = b[idx_start + 1:]

        idx_stop = b.find(b']') 
        value_list = b[:idx_stop].split(b"|")
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
    def __init__(self, key, **argv) -> None:

        self.__dict__['key'] = key
        self.__dict__['_class_signature'] =  "<" + ".".join([type(self).__module__, type(self).__qualname__]) + ">" 

        for keyword in self.KEYWORDS:

            if keyword in argv:

                self.__dict__[keyword] = argv[keyword]

            else:

                self.__dict__[keyword] = None

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

    pass
