import requests
import json
from requests.exceptions import Timeout, HTTPError

http_status = {
    400: HTTPError('The request could not be understood by the server due to malformed syntax.'),
    401: HTTPError('The request requires user authentication.'),
    403: HTTPError('The server understood the request, but is refusing to fulfill it.'),
    404: HTTPError('The server has not found anything matching the Request-URI.'),
    500: HTTPError('The server encountered an unexpected condition which prevented it from fulfilling the request.'),
    504: HTTPError('The server did not receive a timely response from an upstream server it needed to access in order to complete the request.'),
}


class Requestor:

    @staticmethod
    def get(api):
        """Get data from url

        Args:
            api (class): subclass of BaseApi

        Raises:
            Timeout: request timeout
            ValueError: request does not contain valid JSON data
            RuntimeError: request error

        Returns:
            json: response data
        """
        try:
            response = requests.get(
                api.url, headers=api.headers, timeout=api.timeout)
        except Timeout:
            raise Timeout(
                f'The request timed out after {api.timeout} seconds.')

        code = response.status_code
        if code == 200:
            try:
                if api.callback:
                    return api.callback(response.json())
                return response.json()
            except ValueError:
                raise ValueError(
                    'The request does not contain valid JSON data.')
        else:
            raise http_status[code]

    @staticmethod
    def post(api, data):
        """Post data to url

        Args:
            api (class): subclass of BaseApi
            data (dict): json type data

        Raises:
            TypeError: json type data must be dict
            Timeout: request timeout
            ValueError: request does not contain valid JSON data
            RuntimeError: request error

        Returns:
            json: response data
        """
        try:
            if isinstance(data, dict):
                data = json.dumps(data)
            else:
                raise TypeError('data must be dict')
            response = requests.post(
                api.url, headers=api.headers, data=data, timeout=api.timeout)
        except Timeout:
            raise Timeout(
                f'The request timed out after {api.timeout} seconds.')

        code = response.status_code
        if code == 200:
            try:
                if api.callback:
                    return api.callback(response.json())
                return response.json()
            except ValueError:
                return 'The request does not contain valid JSON data.'
        else:
            raise http_status[code]


if __name__ == '__main__':
    pass
