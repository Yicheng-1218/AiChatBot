import random
from time import sleep
from bs4 import BeautifulSoup
from requests import get
from .base_api import BaseApi
from .certify import Certification


_useragent_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0'
]


def get_useragent():
    return random.choice(_useragent_list)


class GoogleSearch(BaseApi):

    def __init__(self, cert) -> None:
        if isinstance(cert, Certification):
            self._key = cert['google_search']['api_key']
            self._cx = cert['google_search']['cx']

    def custom_search(self, term, num_results=10, lang="zh-tw", advanced=False, sleep_interval=0, timeout=5):
        escaped_term = term.replace(" ", "+")
        start = 0
        while start < num_results:
            params = {
                'cx': self._cx,
                'key': self._key,
                'num': num_results+2,
                "hl": lang,
                'q': escaped_term
            }
            headers = {
                "Content-Type": "application/json; charset=UTF-8",
                "User-Agent": get_useragent()
            }
            resp = super().get('https://www.googleapis.com/customsearch/v1',
                               params, headers=headers, timeout=timeout)
            data = resp.json()
            if len(data) == 0:
                break
            for result in data.get('items'):
                title = result.get('title')
                link = result.get('link')
                description = result['pagemap']['metatags'][0].get(
                    'og:description')
                if description and link and title:
                    if start >= num_results:
                        break
                    start += 1
                    if advanced:
                        yield SearchResult(link, title, description)
                    else:
                        yield link
            sleep(sleep_interval)

    def normal_search(self, term, num_results=10, lang="zh-tw", advanced=False, sleep_interval=0, timeout=5):

        escaped_term = term.replace(" ", "+")

        # Fetch
        start = 0
        while start < num_results:
            # Send request
            params = {
                "q": escaped_term,
                "num": num_results + 2,  # Prevents multiple requests
                "hl": lang,
                "start": start,
            }
            headers = {
                "User-Agent": get_useragent()
            }
            resp = super().get("https://www.google.com/search",
                               params, headers=headers, timeout=timeout)

            soup = BeautifulSoup(resp.text, "html.parser")
            result_block = soup.find_all("div", attrs={"class": "g"})
            if len(result_block) == 0:
                break
            for result in result_block:

                link = result.find("a", href=True)
                title = result.find("h3")
                description_box = result.find(
                    "div", {"style": "-webkit-line-clamp:2"})
                if description_box:
                    description = description_box.text
                    if link and title and description:
                        if start >= num_results:
                            break
                        start += 1
                        if advanced:
                            yield SearchResult(link["href"], title.text, description)
                        else:
                            yield link["href"]
            sleep(sleep_interval)


class SearchResult:
    def __init__(self, url, title, description):
        self.url = url
        self.title = title
        self.description = description

    def __repr__(self):
        return f"SearchResult(url={self.url}, title={self.title}, description={self.description})"
