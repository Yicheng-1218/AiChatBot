from lxml import etree
import requests
try:
    from modules.base_api import BaseApi
except:
    import sys
    sys.path.append('C:/Users/cheng/Desktop/Azure Function App')
    from modules.base_api import BaseApi
import re

class FDAInfo(BaseApi):
    
    base_url='https://data.fda.gov.tw/opendata/exportDataList.do?method=ExportData&InfoId=159&logType=5'
        
    @classmethod
    def get(cls):
        response=super().get().json()
        return [e['標題'] for e in response]


class Gov165(BaseApi):   
    base_url='https://165.npa.gov.tw/api/'
    
    
class FraudulentID(Gov165):
    @classmethod
    def get(cls,id):
        url=cls.base_url+'queryLineId/'+id
        return super().get(url).json()
        # print(requests.get(url).json())
    
    @classmethod
    def get_list(cls):
        url=cls.base_url+'lineid/querydata'
        return super().get(url).json()

class FraudulentTEL(Gov165):
    
    @classmethod
    def get(cls,tel:str):
        url=cls.base_url+'query/findFraudTel'
        payload = {'keyWord':tel}
        return super().post(url,payload).json()
    
    @classmethod
    def get_list(cls):
        url=cls.base_url+'query/findFraudTel'
        payload = {'keyWord':''}
        return super().post(url,payload).json()

class FraudulentURL(Gov165):
    PARSE_ERROR=-2
    
    @classmethod
    def get(cls,target):
        url=cls.base_url+'query/findFraudInvestment'
        payload = {'keyWord':''}
        domain=re.search(r"([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}", target)
        if domain is None:
            return cls.PARSE_ERROR
        domain=domain.group().replace('www.','')
        response = super().post(url,payload).json()
        return [element for element in response if domain in element['webUrl']]
    
    @classmethod
    def get_list(cls):
        url=cls.base_url+'query/findFraudInvestment'
        payload = {'keyWord':''}
        return super().post(url,payload).json()
    

def striphtml(data):
        p = re.compile(r'<.*?>')
        return p.sub('', data)
    
class FraudulentInfo(Gov165):
    @classmethod
    def get(cls,query):
        url=cls.base_url+'article/list/rumor'
        
        rlt= super().get(url).json()
        try:
            article_id=[element for element in rlt if query in element['title']][0]['id']
        except:
            return None
        url=cls.base_url+f'article/detail/rumor/{article_id}'
        
        response=super().get(url).json()
        return striphtml(response['content']).strip().replace('\n','')

    @classmethod
    def get_list(self):
        url=self.base_url+'article/list/rumor'
        return super().get(url).json()

class Urlvoid:
    DOMAIN_NOT_FOUND=-1
    PARSE_ERROR=-2
    base_url='https://www.urlvoid.com/scan/'
    _url=''
    
    @classmethod
    def get(cls,url):
        """Get the website trust score"""
        domain=re.search(r"([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}", url)
        if domain is None:
            return cls.PARSE_ERROR
        domain=domain.group().replace('www.','')
        cls._url=cls.base_url+domain
        res=requests.get(cls._url).json()
        root=etree.HTML(res.text)
        detections_counts=root.xpath('//span[@class="label label-success"]/text()')
        if len(detections_counts)<1:
            return cls.DOMAIN_NOT_FOUND
        score=(1-eval(detections_counts[0]))*100
        return score
    
    @property
    def url(self):
        return self._url
    
if __name__ == '__main__':
    # api = FDAInfo.get()
    api=FraudulentID.get('ht354')
    # api=FraudulentTEL.get('+886227581936')
    # api=FraudulentURL.get('peichengstock.com')
    # api=FraudulentInfo.get('謠言')
    # api=Urlvoid.get('https://www.google.com')
    print(api)
    pass