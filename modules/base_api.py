from .requestor import Requestor


class BaseApi:
    def __init__(self, base_url, headers=None, callback=None, timeout=5) -> None:
        self.__url = base_url
        self.callback = callback
        self.timeout = timeout
        self.__data = None
        if headers is None:
            self.headers = {
                'Content-Type': 'application/json; charset=UTF-8'
            }
        else:
            self.headers = headers

    @property
    def url(self):
        return self.__url

    @property
    def data(self):
        return self.__data

    def set_data(self, data):
        self.__data = data

    def set_url(self, url, **kwargs):
        if kwargs:
            self.__url += '?' + \
                '&'.join([f'{key}={value}' for key, value in kwargs.items()])
        else:
            self.__url = url

    @property
    def count(self):
        return len(self.__data)

    def _get(self):
        """Get data from url
            return will be saved in self.__data
        Returns:
            Class: return self
        """
        self.__data = Requestor.get(self)
        return self

    def _post(self, data):
        """Post data to url
            return will be saved in self.__data
        Args:
            data (dict): json type data

        Returns:
            Class: return self
        """
        self.__data = Requestor.post(self, data)
        return self
