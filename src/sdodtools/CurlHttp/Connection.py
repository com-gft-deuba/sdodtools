from .Host import *
from .Auth import *

##############################################################################
##############################################################################

class Connection:

    def __init__(self, server, server_auth=None, proxy=None, proxy_auth=None):

        if not isinstance(server, Server): raise ValueError(f"Expected Server got {type(server)}!")

        if server_auth is not None and not isinstance(server_auth, ServerAuth): raise ValueError(f"Expected ServerAuth got {type(server_auth)}!")

        if not isinstance(proxy, Proxy): raise ValueError(f"Expected Proxy got {type(proxy)}!")

        if proxy_auth is not None and not isinstance(proxy_auth, ProxyAuth): raise ValueError(f"Expected ProxyAuth got {type(proxy_auth)}!")

        self.server = server
        self.server_auth = server_auth
        self.proxy = proxy
        self.proxy_auth = proxy_auth

    def options(self, obfuscate=False):

        options = []

        if self.server is not None: options.extend(self.server.options(obfuscate=obfuscate))

        if self.proxy is not None: options.extend(self.proxy.options(obfuscate=obfuscate))

        return options
