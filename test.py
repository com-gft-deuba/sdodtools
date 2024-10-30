import sys
import os
import urllib

sys.path.insert(1, os.path.join(sys.path[0], 'lib'))
sys.path.insert(1, os.path.join(os.environ['HOME'], 'lib'))

import Crypt
import UrllibCurl
import Cli.Utils

# e = Cli.Utils.get_cli_exception(baseclass=Exception, name='MyException', message='MyMessage', r=1, stdout='STDOUT', stderr='STDERR')
# print(e)
# raise(e)

key1 = Crypt.Keys.KeyIV.generate()
# key2 = Crypt.Keys.KeyIV.generate()
login = Crypt.Secrets.Login.from_key(key=key1, user=b"myuser", password=b"mypassword")
# logincontainer = Crypt.Secrets.SecretContainer(secret=login, domain='AAA', name='BBB', category='CCC')


# print(login.key)
# print(login.user)
# print(login.clearuser)

# # login.key = key2

# # # print(login.domain)
# print(login)
# b = bytes(login)
# print(b)
# o,r = Crypt.Secrets.Login.from_bytes(b, key=key1)
# print(o)
# print(o.key)
# print(o.user)
# print(o.clearuser)

# o,r = Crypt.Secrets.SecretFactory.from_bytes(b)
# print(o)

# print(logincontainer)
# b = bytes(logincontainer)
# o,r = Crypt.Secrets.SecretFactory.from_bytes(b)
# print(o)

# print(logincontainer.user)
# print(logincontainer.clearuser)
# print(logincontainer.domain)



# Proxy mapping: Hostnames to proxy URLs
proxy_mapping = {
    re.compile(r'^(?:https?://)?httpbin.org(?:/|$)'): UrllibCurl.Proxy.ProxyMap(proxy='http://proxy:port', auth=UrllibCurl.Auth.ProxyAuthLogin(login=login))
}

# Create an opener using the custom handler
opener = urllib.request.build_opener(UrllibCurl.Handler.CurlHandler(proxy_mapping))

# Install the opener globally, so all urllib requests use it
urllib.request.install_opener(opener)

# Example usage for HTTP
response = urllib.request.urlopen('http://httpbin.org/get')
print(response.read().decode())
