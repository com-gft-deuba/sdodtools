import urllib.parse

from .Auth import ServerAuth, ProxyAuth, ServerAuthLogin
from ..Crypt import Login

##############################################################################
##############################################################################

class Host:

    @staticmethod
    def _to_str(host, port, scheme):

        if port is None:

            return f'{scheme}://{host}'

        return f'{scheme}://{host}:{port}'

    def __init__(self, host, port=None, scheme=None):

        if scheme is None: scheme = 'https'

        self._host = host
        self._port = port
        self._scheme = scheme
        self._str = self._to_str(self.host, self.port, self.scheme )

    @property
    def host(self): return self._host

    @host.setter
    def host(self, value):
        self._host = value
        self._str = self._to_str(self.host, self.port, self.scheme )

    @property
    def port(self): return self._port

    @port.setter
    def port(self, value):
        self._port = value
        self._str = self._to_str(self.host, self.port, self.scheme )

    @property
    def scheme(self): return self._scheme

    @scheme.setter
    def scheme(self, value):
        self._scheme = value
        self._str = self._to_str(self.host, self.port, self.scheme )

    def __str__(self): return self._str

##############################################################################
##############################################################################

class Server(Host):

    @classmethod
    def from_url(cls, url, server_auth=None, proxy=None):

        parsed = urllib.parse.urlparse(url)
        login = None

        if parsed.username is not None and parsed.password is not None:

            login = Login(user=parsed.username.encode(), password=parsed.password.encode())
            login = ServerAuthLogin(secret=login)

        return cls(host=parsed.hostname, scheme=parsed.scheme, port=parsed.port, server_auth=login)

    def __init__(self, host, port=None, scheme=None, server_auth=None):

        if server_auth is not None and not isinstance(server_auth, ServerAuth): raise ValueError(f"Expected ServerAuth got {type(server_auth)}!")

        super().__init__(host=host, port=port, scheme=scheme)

        self.server_auth = server_auth

    def options(self, obfuscate=False):

        if self.server_auth is not None:

            return self.server_auth.options(obfuscate=obfuscate)
        
        return []

##############################################################################
##############################################################################

class Proxy(Host):

    @staticmethod
    def _to_str(host, port, scheme):

        if port is None:

            return host

        return f'{host}:{port}'

    def __init__(self, host, port=None, scheme=None, proxy_auth=None):

        if proxy_auth is not None and not isinstance(proxy_auth, ProxyAuth): raise ValueError(f"Expected ProxyAuth got {type(proxy_auth)}!") 

        super().__init__(host=host, port=port, scheme=scheme)

        self.proxy_auth = proxy_auth

    def options(self, obfuscate=False):

        options = ['--proxy', str(self), '--proxy-insecure', '--suppress-connect-headers']

        if self.proxy_auth is not None:

            options.extend(self.proxy_auth.options(obfuscate=obfuscate))
        
        return options
