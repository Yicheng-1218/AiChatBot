import random
from time import sleep, time
from bs4 import BeautifulSoup
from .base_api import BaseApi
from .certify import Certification
import pyuseragents


class GoogleSearch(BaseApi):

    def __init__(self, cert) -> None:
        if isinstance(cert, Certification):
            self._key = cert['google_search']['api_key']
            self._cx = cert['google_search']['cx']

    def custom_search(self, term, num_results=10, lang="zh-tw", advanced=False, sleep_interval=0, timeout=5):
        escaped_term = term.replace(" ", "+")

        time_stamp = time()
        start = 0
        while start < num_results:
            if time()-time_stamp > timeout:
                break
            params = {
                'cx': self._cx,
                'key': self._key,
                'num': num_results+2,
                "hl": lang,
                'q': escaped_term
            }
            headers = {
                "Content-Type": "application/json; charset=UTF-8",
                "User-Agent": pyuseragents.random()
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
        time_stamp = time()
        start = 0
        while start < num_results:
            if time()-time_stamp > timeout:
                break
            # Send request
            params = {
                "q": escaped_term,
                "num": num_results + 2,  # Prevents multiple requests
                "hl": lang,
                "start": start,
            }
            headers = {
                "User-Agent": pyuseragents.random()
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

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, SearchResult):
            return self.title == __value.title
        return False

    def __hash__(self) -> int:
        return hash(self.title)
