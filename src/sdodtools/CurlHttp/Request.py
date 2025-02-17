import urllib.request
from ..Cli import Command

##############################################################################
##############################################################################

class Request:

    def __init__(self, connection, method='GET', base_url=None, base_headers=None, base_query=None):
        self.connection = connection
        self.method = method
        self.base_url = base_url
        self.base_headers = base_headers
        self.base_query = base_query

    def run(self, url=None, parameters=None, headers=None, data=None):

        full_url = self.get_url(url=url, parameters=parameters, headers=headers)

        if self.base_headers is not None:

            headers = self.base_headers.get_headers(headers=headers)

        else:

            headers = HeaderPart._toarray(headers)

        headers = [ ('--header', f'{x[0]}: {x[1]}') if x[1] is not None else ('--header', x[0]) for x in headers]
        headers = [ x for xs in headers for x in xs]

        cmd = []
        cmd.append('curl')
        cmd.append('--silent')
        cmd.append('--insecure')
        cmd.append('--include')
        cmd.extend(self.connection.options())
        cmd.append('--request')
        cmd.append(self.method)
        cmd.extend(headers)
        cmd.append(full_url)

        result = Command(cmd=cmd)
        reply = self._parse_response(result.stdout, full_url)
        return reply, result


    def get_url(self, url=None, parameters=None, headers=None):

        full_url = str(self.connection.server)

        if self.base_url is not None: 

            if self.base_url.startswith('/'):

                full_url = f'{full_url}{self.base_url}'

            else:
                
                full_url = f'{full_url}/{self.base_url}'

        if url is not None:
            
            if url.startswith('/'):

                full_url = f'{full_url}{url}'

            else:
                
                full_url = f'{full_url}/{url}'

        query_parameters = []

        if self.base_query is not None:

            query_parameters = self.base_query.get_parameters(parameters=parameters)

        else:

            query_parameters = QueryPart._toarray(parameters)

        if len(query_parameters) > 0:

            separator = '?'

            for parameter in query_parameters:

                if parameter[1] is not None:

                    full_url = f'{full_url}{separator}{parameter[0]}={parameter[1]}'

                else:

                    full_url = f'{full_url}{separator}{parameter[0]}'

                separator = '&'

        return full_url

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
