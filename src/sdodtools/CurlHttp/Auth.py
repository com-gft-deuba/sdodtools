##############################################################################
##############################################################################
### Classes
##############################################################################
##############################################################################

from .. import Crypt

##############################################################################
##############################################################################

class ServerAuth:

    def __init__(self, secret) -> None: self.secret = secret

    @classmethod
    def from_secret(cls, secret):
            
            if isinstance(secret, Crypt.Secrets.Container): _secret = secret.secret
            else: _secret = secret
    
            if isinstance(_secret, Crypt.Secrets.Login): return ServerAuthLogin(secret=secret)
    
            if isinstance(_secret, Crypt.Secrets.Token): return ServerAuthToken(secret=secret)
    
            if isinstance(_secret, Crypt.Secrets.Cookie): return ServerAuthCookie(secret=secret)
    
            raise ValueError(f"Unknown secret type {type(_secret)}!")

    def options(self, obfuscate=False): return []

class ServerAuthNone(ServerAuth):

    def __init__(self, secret=None) -> None: super().__init__(secret=secret)

class ServerAuthLogin(ServerAuth):

    def options(self, obfuscate=False): return ["--basic", "--user", f"{self.secret.clearuser.decode()}:{self.secret.clearpassword.decode() if not obfuscate else '***' }"]

class ServerAuthDigest(ServerAuthLogin):

    def options(self, obfuscate=False): return ["--digest", "--user", f"{self.login.clearuser.decode()}:{self.login.clearpassword.decode() if not obfuscate else '***' }"]

class ServerAuthNTLM(ServerAuthLogin):

    def options(self, obfuscate=False): return ["--ntlm", "--user", f"{self.secret.clearuser.decode()}:{self.secret.clearpassword.decode() if not obfuscate else '***' }"]

class ServerAuthCookie(ServerAuth):

    def options(self, obfuscate=False): return ["--header", f"{self.secret.header.decode()}: {self.secret.value.decode() if not obfuscate else '***' }"]

class ServerAuthToken(ServerAuth):

    def options(self, obfuscate=False): return ["--header", f"{self.secret.header.decode()}: {self.secret.token.decode() if not obfuscate else '***' }"]

##############################################################################
##############################################################################

class ProxyAuth:

    def __init__(self, secret) -> None:

        self.secret = secret

    @classmethod
    def from_secret(cls, secret):
    
            if isinstance(secret, Crypt.Secrets.Container): _secret = secret.secret
            else: _secret = secret

            if isinstance(_secret, Crypt.Secrets.Login): return ProxyAuthLogin(secret=secret)
    
            if isinstance(_secret, Crypt.Secrets.Token): return ProxyAuthToken(secret=secret)
    
            if isinstance(_secret, Crypt.Secrets.Cookie): return ProxyAuthCookie(secret=secret)
    
            raise ValueError(f"Unknown secret type {type(_secret)}!")

    def options(self, obfuscate=False): return []

class ProxyAuthNone(ProxyAuth):

    def __init__(self, secret=None) -> None: super().__init__(secret=secret)

class ProxyAuthLogin(ProxyAuth):

    def options(self, obfuscate=False): return ["--proxy-basic", "--proxy-user", f"{self.secret.clearuser.decode()}:{self.secret.clearpassword.decode() if not obfuscate else '***' }"]

class ProxyAuthDigest(ProxyAuthLogin):

    def options(self, obfuscate=False): return ["--proxy-digest", "--proxy-user", f"{self.login.clearuser.decode()}:{self.login.clearpassword.decode() if not obfuscate else '***' }"]

class ProxyAuthNTLM(ProxyAuthLogin):

    def options(self, obfuscate=False): return ["--proxy-ntlm", "--proxy-user", f"{self.secret.clearuser.decode()}:{self.secret.clearpassword.decode() if not obfuscate else '***' }"]

class ProxyAuthCookie(ProxyAuth):

    def options(self, obfuscate=False): return ["--proxy-header", f"{self.secret.header.decode()}: {self.secret.value.decode() if not obfuscate else '***' }"]

class ProxyAuthToken(ProxyAuth):

    def options(self, obfuscate=False): return ["--proxy-header", f"{self.secret.header.decode()}: {self.secret.token.decode() if not obfuscate else '***' }"]

##############################################################################
##############################################################################

class NoAuth(ServerAuth, ProxyAuth):

    def __init__(self) -> None:

        pass

    def options(self, obfuscate=False): return []

