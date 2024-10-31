##############################################################################
##############################################################################
### Classes
##############################################################################
##############################################################################

##############################################################################
##############################################################################

class Auth:

    def __init__(self, secret) -> None: self.secret = secret

    def options(self): return []

class AuthNone(Auth):

    def __init__(self, secret=None) -> None: super().__init__(secret=secret)

class AuthLogin(Auth):

    def options(self): return ["--basic", "--user", f"{self.secret.clearuser.decode()}:{self.secret.clearpassword.decode()}"]

class AuthDigest(AuthLogin):

    def options(self): return ["--digest", "--user", f"{self.login.clearuser.decode()}:{self.login.clearpassword.decode()}"]

class AuthNTLM(AuthLogin):

    def options(self): return ["--ntlm", "--user", f"{self.secret.clearuser.decode()}:{self.secret.clearpassword.decode()}"]

class AuthCookie(Auth):

    def options(self): return ["--header", f"{self.secret.header.decode()}: {self.secret.value.decode()}"]

##############################################################################
##############################################################################

class ProxyAuth:

    def __init__(self, secret) -> None:

        self.secret = secret

    def options(self): return []

class ProxyAuthNone(ProxyAuth):

    def __init__(self, secret=None) -> None: super().__init__(secret=secret)

class ProxyAuthLogin(ProxyAuth):

    def options(self): return ["--proxy-basic", "--proxy-user", f"{self.secret.clearuser.decode()}:{self.secret.clearpassword.decode()}"]

class ProxyAuthDigest(ProxyAuthLogin):

    def options(self): return ["--proxy-digest", "--proxy-user", f"{self.login.clearuser.decode()}:{self.login.clearpassword.decode()}"]

class ProxyAuthNTLM(ProxyAuthLogin):

    def options(self): return ["--proxy-ntlm", "--proxy-user", f"{self.secret.clearuser.decode()}:{self.secret.clearpassword.decode()}"]

class ProxyAuthCookie(ProxyAuth):

    def options(self): return ["--proxy-header", f"{self.secret.header.decode()}: {self.secret.value.decode()}"]
