import requests


class BaseApi:
    DEFAULT_TIMEOUT = 10
    _url = ''
    _data = None
    _headers = {
        'Content-Type': 'application/json; charset=UTF-8'
    }

    @property
    def url(self):
        return self._url

    @property
    def data(self):
        return self._data

    @property
    def count(self):
        return len(self._data)

    @classmethod
    def get(cls, url='', query=None, headers=None, timeout=DEFAULT_TIMEOUT):
        if headers is None:
            headers = cls._headers
        if url != '':
            cls._url = url
            if query is not None:
                cls._url = url_query(url, **query)
        elif hasattr(cls, 'base_url'):
            cls._url = cls.base_url
        else:
            raise ValueError('url must be provided')

        response = requests.get(
            cls._url,
            headers=headers,
            timeout=timeout
        )
        response.raise_for_status()
        if 'json' in response.headers.get('Content-Type'):
            cls._data = response.json()
        return response

    @classmethod
    def post(cls, url='', data=None, headers=None, timeout=DEFAULT_TIMEOUT):
        if headers is None:
            headers = cls._headers
        if url != '':
            cls._url = url
        elif hasattr(cls, 'base_url'):
            cls._url = cls.base_url
        else:
            raise ValueError('url must be provided')
        response = requests.post(
            cls._url,
            headers=headers,
            timeout=timeout,
            json=data)
        response.raise_for_status()
        if 'json' in response.headers.get('Content-Type'):
            cls._data = response.json()
        return response


def url_query(url, **kwargs):
    if kwargs is not None:
        url += '?' + \
            '&'.join([f'{key}={value}' for key, value in kwargs.items()])
    return url
