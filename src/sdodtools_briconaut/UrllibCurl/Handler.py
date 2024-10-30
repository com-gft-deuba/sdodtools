import urllib.request
import subprocess
import io
import email
from http.client import HTTPMessage
import Cli.Utils
import sys

class CurlHandler(urllib.request.HTTPHandler):

    def __init__(self, proxy_mapping):

        self.proxy_mapping = proxy_mapping

    def http_open(self, req):

        return self.curl_open(req, 'http')

    def https_open(self, req):

        return self.curl_open(req, 'https')

    def curl_open(self, req, scheme):

        curl_command = ['curl', '--silent', '--insecure', '--include', '--request', req.get_method()]

        proxy = self._get_proxy(req.host)

        if proxy is not None:

            curl_command.append('--proxy-insecure')
            curl_command.append('--suppress-connect-headers')
            curl_command.extend(['--proxy', proxy.proxy])
            curl_command.extend(proxy.auth.options())

        for key, value in req.headers.items():

            curl_command.extend(['--header', f'{key}: {value}'])

        url = f"{scheme}://{req.host}{req.selector}"
        curl_command.append(url)

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

        return self.proxy_mapping.get(host)

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
