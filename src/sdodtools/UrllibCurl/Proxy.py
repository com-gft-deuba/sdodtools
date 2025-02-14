##############################################################################
##############################################################################
### Classes
##############################################################################
##############################################################################

##############################################################################
##############################################################################

import re

class ProxyMap:

    def __init__(self, host, proxy, auth):

        if isinstance(host, str): host = re.compile(f'^{host}$')

        self.host = host
        self.proxy = proxy
        self.auth = auth

    def match(self, host): return self.host.match(host) is not None

class ProxyMaps:

    def __init__(self, proxy_maps=None):

        if proxy_maps is None: proxy_maps = []

        self.proxy_maps = proxy_maps

    def add(self, host, proxy, auth=None):

        self.proxy_maps.append(ProxyMap(host=host, proxy=proxy, auth=auth))

    def get(self, host):

        for p in self.proxy_maps:

            if p.match(host): return p

        return None

