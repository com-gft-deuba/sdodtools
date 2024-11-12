import urllib.request
import subprocess
import pipes
import io
import email

from .. import Cli

##############################################################################
##############################################################################
### Classes
##############################################################################
##############################################################################

##############################################################################
##############################################################################

class CurlHandler(urllib.request.HTTPHandler):

    def __init__(self, proxy_maps=None, server_auth=None):

        self.proxy_maps = proxy_maps
        self.server_auth = server_auth

    def http_open(self, req):
        print("XXXXXXXXXXXXXXXXXXXX")
        return self.curl_open(req, 'http')

    def https_open(self, req):
        print("XXXXXXXXXXXXXXXXXXXX")
        return self.curl_open(req, 'https')

    def _build_curl_command(self, req, scheme, obfuscate=False):

        curl_command = ['curl', '--silent', '--insecure', '--include', '--request', req.get_method()]

        if self.server_auth is not None:

            curl_command.extend(self.server_auth.options(obfuscate=obfuscate))

        proxy = self._get_proxy(req.host)

        if proxy is not None:

            curl_command.append('--proxy-insecure')
            curl_command.append('--suppress-connect-headers')
            curl_command.extend(['--proxy', proxy.proxy])

            if proxy.auth is not None:
                
                curl_command.extend(proxy.auth.options(obfuscate=obfuscate))

        for key, value in req.headers.items():

            curl_command.extend(['--header', f'{key}: {value}'])

        url = f"{scheme}://{req.host}{req.selector}"
        curl_command.append(url)

        return curl_command

    def curl_open(self, req, scheme):
        print("XXXXXXXXXXXXXXXXXXXX")
        curl_command = self._build_curl_command(req, scheme, obfuscate=False)

        try:

            cmd = subprocess.Popen(args=curl_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=False)
            data=''
            (stdout, stderr) = cmd.communicate(input=data)
            status = cmd.returncode

            if status != 0: raise Cli.Utils.CliException(message='Curl command failed.', cmd=cmd, r=status, stdout=stdout, stderr=stderr)

            return self._parse_response(stdout, url)
        
        except subprocess.CalledProcessError as e:

            raise urllib.error.URLError(e) from None

    def _get_proxy(self, host):

        if self.proxy_maps is None: return None

        return self.proxy_maps.get(host)

    def _parse_response(self, response_data, url):

        # Split headers and body

        header_data, body = response_data.split(b'\r\n\r\n', 1)
        
        # Parse headers into an HTTPMessage object
        header_lines = header_data.split(b'\r\n')
        code = int(header_lines[0].split(b' ')[1])
        headers = email.message_from_bytes(b'\r\n'.join(header_lines[1:]))
        # Create a mock response object
        response = urllib.response.addinfourl(
            io.BytesIO(body),
            headers=headers,
            url=url,
            code=code
        )
        # Set the msg attribute
        response.msg = body

        return response
