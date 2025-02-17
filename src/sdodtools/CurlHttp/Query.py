##############################################################################
##############################################################################

class Headers:

    @staticmethod
    def _toarray(headers): 
        if headers is None or len(headers) == 0: return []

        return [(x, None) if isinstance(x, str) else (x[0], None) if len(x) == 1 else (x[0], x[1]) for x in headers]
    
    def __init__(self, headers):

        self.headers = self._toarray(headers)

    def __len__(self): return len(self.headers)

    def __iter__(self): return iter(self.headers)

    def get_headers(self, headers=None):

        all_headers = []

        if self.headers is not None:

            all_headers = self.headers[:]

        if headers is not None: 

            headers = self._toarray(headers)
            all_headers.extend(headers)

        return all_headers

##############################################################################
##############################################################################

class Query:

    @staticmethod
    def _toarray(parameters): 

        if parameters is None or len(parameters) == 0: return []

        return [(x, None) if isinstance(x, str) else (x[0], None) if len(x) == 1 else (x[0], x[1]) for x in parameters]

    def __init__(self, parameters):

        self.parameters = self._toarray(parameters)

    def __len__(self): return len(self.parameters)

    def __iter__(self): return iter(self.parameters)

    def get_parameters(self, parameters=None):

        all_parameters = []

        if self.parameters is not None:

            all_parameters = self.parameters[:]

        if parameters is not None: 

            parameters = self._toarray(parameters)
            all_parameters.extend(parameters)

        return all_parameters
