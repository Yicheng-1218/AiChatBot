# try:
#     from modules.base_api import BaseApi
# except:
#     import sys
#     sys.path.append('c:/Users/cheng/Desktop/Azure Function App')
#     from modules.base_api import BaseApi
from modules.base_api import BaseApi
import re

class FDAInfo(BaseApi):
    def __init__(self,callback=None) -> None:
        base_url='https://data.fda.gov.tw/opendata/exportDataList.do?method=ExportData&InfoId=159&logType=5'
        super().__init__(base_url,callback=callback)
        
    def get(self):
        self.callback=lambda x: [e['標題'] for e in x]
        return self._get()


class Gov165(BaseApi):
    def __init__(self,callback=None) -> None:
        self.base_url='https://165.npa.gov.tw/api/'
        super().__init__(self.base_url,callback=callback)
    
class FraudulentID(Gov165):
    def get(self,id):
        url=self.base_url+'queryLineId/'+id
        self.set_url(url)
        return self._get()
    
    def get_list(self):
        url=self.base_url+'lineid/querydata'
        self.set_url(url)
        return self._get()

class FraudulentTEL(Gov165):
    def get(self,tel):
        url=self.base_url+'query/findFraudTel'
        self.set_url(url)
        payload = {'keyWord':tel}
        return self._post(payload)
    
    def get_list(self):
        url=self.base_url+'query/findFraudTel'
        self.set_url(url)
        return self._post({'keyWord':''})

class FraudulentURL(Gov165):
    def get(self,url):
        url=self.base_url+'query/findFraudInvestment'
        self.callback=lambda x:[e for e in x if url in e['webUrl']]
        return self._post({'keyWord':''})

    def get_list(self):
        url=self.base_url+'query/findFraudInvestment'
        self.set_url(url)
        return self._post({'keyWord':''})
    

class FraudulentInfo(Gov165):
    def striphtml(self,data):
        p = re.compile(r'<.*?>')
        return p.sub('', data)
    
    def get(self,query):
        url=self.base_url+'article/list/rumor'
        self.set_url(url)
        self._get()
        try:
            article_id=[element for element in self.data if query in element['title']][0]['id']
        except:
            self.set_data('Can not find article')
            return self
        url=self.base_url+f'article/detail/rumor/{article_id}'
        self.set_url(url)
        self.callback=lambda x:self.striphtml(x['content']).strip().replace('\n','')
        return self._get()

    def get_list(self):
        url=self.base_url+'article/list/rumor'
        self.set_url(url)
        return self._get()


if __name__ == '__main__':
    # api = FDAInfo().get()
    # api=FraudulentID().get('ht354')
    api=FraudulentTEL().get('+886227581936')
    # api=FraudulentURL().get('peichengstock.com')
    # api=FraudulentInfo().get('疫苗')
    print(api.data)