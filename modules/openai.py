from .base_api import BaseApi
from .certify import Certification
import requests
import json

DEFAULT_API_ENDPOINT = 'https://api.openai.com/'


class ChatGPT(BaseApi):
    DEFAULT_PATH = 'v1/chat/completions'
    DEFAULT_TIMEOUT = 120
    DEFAULT_MODEL = 'gpt-3.5-turbo'

    def __init__(self, cert, headers=None, callback=None, timeout=DEFAULT_TIMEOUT, model=DEFAULT_MODEL, endpoint=DEFAULT_API_ENDPOINT,prompt=None) -> None:
        url = endpoint+self.DEFAULT_PATH
        if isinstance(cert, Certification):
            self.api_key = cert['OpenAI']['api_key']
        else:
            raise TypeError('cert must be Certification object')
        
        if prompt is  not None:
            try:
                self.prompt=json.load(open('./prompt.json'))
            except FileNotFoundError:
                if isinstance(prompt,dict):
                    self.prompt=prompt
                else:
                    raise TypeError('prompt must be dict or json file')

        self.model = model
        if headers is None:
            headers = {
                'Content-Type': 'application/json; charset=UTF-8',
                'Authorization': 'Bearer ' + self.api_key
            }

        super().__init__(url, headers, callback, timeout)

    def send_messages(self, messages):
        if not isinstance(messages, (list, tuple)):
            messages = [messages]

        data = {
            'model': self.model,
            'messages': [message.to_dict() for message in messages],
            # 
        }

        # self.callback = lambda x: x['choices'][0]['message']['content']
        self._post(data=data)

    def get_reply(self):
        try:
            return self.data
        except ValueError:
            return 'The request does not contain valid JSON data.'


class GPTddic(BaseApi):
    url='http://kafka-middle-ddic2023ws.apps.digiwincloud.com/api/ai/RH'
    
    def __init__(self,prompt=None) -> None:
        if prompt is  not None:
            try:
                self.prompt=json.load(open('./prompt.json'))
            except FileNotFoundError:
                if isinstance(prompt,dict):
                    self.prompt=prompt
                else:
                    raise TypeError('prompt must be dict or json file')
        
        super().__init__(self.url,timeout=120)
    
    

    # def analyze_message(self,message):
    #     data={
    #         "key":"0",
    #         "data": {
    #             "topic": "AI",
    #             "method": "ChatGPT",
    #             "data": {
    #                 "prompt": [
    #                     {
    #                         "role":"system",
    #                         "content":"""I would like you to play the role of a language expert and assist me in determining the intention of my input messages and some related key information.
    #                         For example:
    #                         1. Is this a fraudulent phone call? 0926444326 You will help me determine it as Inquire About Fraudulent TEL and label the phone number as TEL the label must be require to determine intent.
    #                         2. Is this website problematic? https://www.lorem.com You will help me determine it as Inquire About Fraudulent URL and label the URL as URL the label must be require to determine intent.
    #                         3. Is this a fraudulent account ID? aawx1234 You will help me determine it as Inquire About Fraudulent ID and label aawx1234 as ID the label must be require to determine intent.
    #                         4. Regarding food, drugs, and cosmetics, determine it as Inquire About Food and Drug, entities=[]. 
    #                         5. Other types of inquiries are classified as Other Inquiries.
    #                         6. Meaningless content such as greeting messages is classified as None, entities=[] .
    #                         All intentions can only be categorized as Inquire About Fraudulent ID, Inquire About Fraudulent TEL, Inquire About Fraudulent URL, Inquire About Food and Drug, Other Inquiries, and None.
    #                         Please use only these intention types.When answering, please use only the JSON format, The format should be {\"query\" ... ,\"intent\": ..., \"entities\": [{\"category\": ... , \"text\":...]}.
    #                         And avoid excessive explanations or descriptions. My first question is """+message
    #                     }
    #                 ]
    #             },
    #             "temperature": 0.7,
    #             "top_p": 1
    #         }
    #     }
    #     self._post(data=data)
        
    
    def send_messages(self, messages):
        if not isinstance(messages, (list, tuple)):
            messages = [messages]
        
        if self.prompt is not None:
            prompt=self.prompt['system']
            messages.insert(0,GptMessage('system',prompt))

        data = {
                "key":"0",
                "data":{
                    "topic":"AI",
                    "method":"ChatGPT",
                    "data":{
                        "prompt":[msg.to_dict() for msg in messages]
                    },
                    "temperature":0.7,
                    "top_p":1
                }
            }
        self._post(data=data)
        
    def get_reply(self):
        try:
            return self.data
        except ValueError:
            return 'The request does not contain valid JSON data.'

class GptMessage:
    def __init__(self, role: str, context: str):
        assert role in ['user', 'system',
                        'assistant'], 'role must be user, system or assistant'
        self.role = role
        self.context = context

    def to_dict(self):
        return {
            'role': self.role,
            'content': self.context
        }


if __name__ == '__main__':
    # key = json.load(open('./api_key.json'))['OpenAI']['api_key']

    gpt = ChatGPT(Certification('./api_key.json'))
    Messages = [
        GptMessage('system', """You are an anti-fraud expert who is familiar with various fraud schemes.
                You will refer to the articles I provide and summarize them concisely.
                And always respond in Chinese Traditional.
                You need to do the first thing is Self introduction.
                """),
        GptMessage('user', '這是詐騙電話嗎? +886963535138')
    ]
    gpt.send_messages(Messages)
    print(gpt.get_reply())
    pass
