##############################################################################
##############################################################################
### Classes
##############################################################################
##############################################################################


##############################################################################
##############################################################################

class AuthNone:

    def __init__(self) -> None:

        pass

    def options(self): return []

class AuthLogin:

    def __init__(self, login) -> None:

        self.login = login

    def options(self): return ["--basic", "--user", f"{self.login.clearuser.decode()}:{self.login.clearpassword.decode()}"]

class AuthDigest:

    def __init__(self, login) -> None:

        self.login = login

    def options(self): return ["--digest", "--user", f"{self.login.clearuser.decode()}:{self.login.clearpassword.decode()}"]

class AuthNTLM:

    def __init__(self, login) -> None:

        self.login = login

    def options(self): return ["--ntlm", "--user", f"{self.login.clearuser.decode()}:{self.login.clearpassword.decode()}"]

class AuthCookie:

    def __init__(self, cookie) -> None:
        self.login = cookie

    def options(self): return ["--header", f"{self.cookie.header.decode()}: {self.cookie.value.decode()}"]

##############################################################################
##############################################################################

class ProxyAuthNone:

    def __init__(self) -> None:
        
        pass

    def options(self): return []

class ProxyAuthLogin:

    def __init__(self, login) -> None:
        self.login = login

    def options(self): return ["--proxy-basic", "--proxy-user", f"{self.login.clearuser.decode()}:{self.login.clearpassword.decode()}"]

class ProxyAuthDigest:

    def __init__(self, login) -> None:
        self.login = login

    def options(self): return ["--proxy-digest", "--proxy-user", f"{self.login.clearuser.decode()}:{self.login.clearpassword.decode()}"]

class ProxyAuthNTLM:

    def __init__(self, login) -> None:
        self.login = login

    def options(self): return ["--proxy-ntlm", "--proxy-user", f"{self.login.clearuser.decode()}:{self.login.clearpassword.decode()}"]

class ProxyAuthCookie:

    def __init__(self, cookie) -> None:
        self.login = cookie

    def options(self): return ["--proxy-header", f"{self.cookie.header.decode()}: {self.cookie.value.decode()}"]

