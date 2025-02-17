import subprocess
import email
import urllib.response
import collections

##############################################################################
##############################################################################

CommandResults = collections.namedtuple('CommandResults', ['status', 'stdout', 'stderr'])

##############################################################################
##############################################################################

class CommandException(subprocess.CalledProcessError):

    @classmethod
    def from_result(cls, message=None, cmd=None, status=None, stdout=None, stderr=None, is_success=lambda r, stdout, stderr: r ==0):

        if is_success(status, stdout, stderr): return

        return cls(message, cmd, status, stdout, stderr)

    def __init__(self, message, cmd, status=None, stdout='', stderr=''):

        subprocess.CalledProcessError.__init__(self, status, cmd, stdout, stderr)

        message += "\n"
        message += f"Exit status was ({status})\n"
        message += f"STDOUT was:\n"

        for line in stdout.split(b"\n"): message += f"    {line.decode()}\n"

        message += f"STDERR was:\n"

        for line in stderr.split(b"\n"): message += f"    {line.decode()}\n"

        self.message = message
        self.status = status
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self): return self.message

##############################################################################
##############################################################################

class Command:

    def __init__(self, cmd, data=None):

        self.cmd = cmd
        self.data = data

    def __str__(self): return "'" + "' '".join(self.cmd) + "'"

    def run(self, parameters=None, data=None):

        if self.cmd is None: cmd = []
        else: cmd = self.cmd[:]

        if parameters is not None: cmd.extend(parameters)

        if data is None: data = self.data
        if data is None: data = ''

        try:

            cmd = subprocess.Popen(args=cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=False)

            (stdout, stderr) = cmd.communicate(input=data)
            status = cmd.returncode

        except subprocess.CalledProcessError as e:

            raise CommandException(message='Calling command failed.', cmd=cmd, status=status, stdout=stdout, stderr=stderr) from e

        if status != 0: raise CommandException(message='Command failed.', cmd=cmd, status=status, stdout=stdout, stderr=stderr)

        return CommandResults(status=status, stdout=stdout, stderr=stderr) 
        



    # def __init__(self, host, url, method='get', scheme='https', base_url='', query=None, headers=None, proxy_maps=None, server_auth=None, payload=None):

    #     self.host = host
    #     self.url = url
    #     self.method = method
    #     self.scheme = scheme
    #     self.base_url = base_url
    #     self.query = query
    #     self.headers = headers
    #     self.proxy_maps = proxy_maps
    #     self.server_auth = server_auth
    #     self.payload = payload

    # def _build_curl_command(self, host=None, url=None, method=None, scheme=None, base_url=None, query=None, headers=None, proxy_maps=None, server_auth=None, payload=None, obfuscate=False):

    #     if host is None: host = self.host
    #     if host is None: raise ValueError('Host is required.')
    #     if url is None: url = self.url
    #     if url is None: url = ''
    #     if method is None: method = self.method
    #     if method is None: method = 'GET'
    #     if scheme is None: scheme = self.scheme
    #     if scheme is None: scheme = 'https'
    #     if base_url is None: base_url = self.base_url
    #     if base_url is None: base_url = ''
    #     if query is None: method = self.query
    #     if headers is None: headers = self.headers
    #     if proxy_maps is None: method = self.proxy_maps
    #     if server_auth is None: server_auth = self.server_auth
    #     if payload is None: payload = self.payload

        # curl_command = ['curl', '--silent', '--insecure', '--include', '--request', method ]

        # if self.server_auth is not None:

        #     curl_command.extend(self.server_auth.options(obfuscate=obfuscate))

        # proxy = None

        # if proxy_maps is not None:

        #     proxy = proxy_maps.get(host)

        # if proxy is not None:

        #     curl_command.append('--proxy-insecure')
        #     curl_command.append('--suppress-connect-headers')
        #     curl_command.extend(['--proxy', proxy.proxy])

        #     if proxy.auth is not None:
                
        #         curl_command.extend(proxy.auth.options(obfuscate=obfuscate))

        # if headers is not None:

        #     for header_info in headers:

        #         curl_command.extend(['--header', f'{header_info[0]}: {header_info[1]}'])

        # if payload is not None: curl_command.extend(['--data', payload])

        # target_url = f"{scheme}://{host}"

        # if base_url is not None and base_url != '': target_url = f"{target_url}/{base_url}"
        # if url is not None and url != '': target_url = f"{target_url}/{url}"

        # if query is not None:

        #     separator = '?' if '?' not in target_url else '&'

        #     for query_info in query:

        #         if(isinstance(query_info, str)): target_url = f"{target_url}{separator}{query_info}"

        #         elif len(query_info) == 1: target_url = f"{target_url}{separator}{query_info[0]}"

        #         else: target_url = f"{target_url}{separator}{query_info[0]}={query_info[0]}"

        # return curl_command

    # def run(self, host=None, url=None, method=None, scheme=None, base_url=None, query=None, headers=None, proxy_maps=None, server_auth=None, payload=None, obfuscate=False):

    #     curl_command = self._build_curl_command(host=host, url=url, method=method, scheme=scheme, base_url=base_url, query=query, headers=headers, proxy_maps=proxy_maps, server_auth=server_auth, payload=payload, obfuscate=obfuscate)

    #     try:

    #         cmd = subprocess.Popen(args=curl_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=False)
    #         data=''
    #         (stdout, stderr) = cmd.communicate(input=data)
    #         status = cmd.returncode

    #         if status != 0: raise Cli.Utils.CliException(message='Curl command failed.', cmd=cmd, r=status, stdout=stdout, stderr=stderr)

    #         return self._parse_response(stdout, url)
        
    #     except subprocess.CalledProcessError as e:

    #         raise urllib.error.URLError(e) from None

    # def _parse_response(self, response_data, url):

    #     # Split headers and body

    #     header_data, body = response_data.split(b'\r\n\r\n', 1)
        
    #     # Parse headers into an HTTPMessage object
    #     header_lines = header_data.split(b'\r\n')
    #     code = int(header_lines[0].split(b' ')[1])
    #     headers = email.message_from_bytes(b'\r\n'.join(header_lines[1:]))
    #     # Create a mock response object
    #     response = urllib.response.addinfourl(
    #         io.BytesIO(body),
    #         headers=headers,
    #         url=url,
    #         code=code
    #     )
    #     # Set the msg attribute
    #     response.msg = body

    #     return response
