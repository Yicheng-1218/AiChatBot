from .base_api import BaseApi
from .certify import Certification


class GoogleSearch(BaseApi):
    def __init__(self, cert, item_num=3, callback=None, timeout=15) -> None:
        self.base_url = 'https://www.googleapis.com/customsearch/v1'

        if isinstance(cert, Certification):
            self.__key = cert['google_search']['api_key']
            self.__cx = cert['google_search']['cx']
        else:
            raise TypeError('cert must be Certification object')
        self.num = item_num
        super().__init__(self.base_url, callback=callback, timeout=timeout)

    def format_data(self, data):

        try:
            return {
                'title': data['title'],
                'URL': data['link'],
                'description': data['pagemap']['metatags'][0]['og:description']
            }
        except:
            pass

    def get(self, query):
        api_query = {
            'cx': self.__cx,
            'key': self.__key,
            'num': self.num,
            'q': query,
        }
        self.set_url(self.base_url, **api_query)
        # print(self.url)
        self.callback = lambda x: [
            self.format_data(k) for k in x.get('items', [])]
        return self._get()
