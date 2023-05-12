from .base_api import BaseApi
from .certify import Certification
import logging


class LineBotApi(BaseApi):
    DEFAULT_API_ENDPOINT = 'https://api.line.me'
    DEFAULT_TIMEOUT = 10

    def __init__(self, cert) -> None:
        if isinstance(cert, Certification):
            self.channel_access_token = cert['Line']['channel_access_token']
        # self.channel_access_token = os.environ['Line']['channel_access_token']

        self.headers = {
            'Content-Type': 'application/json; charset=UTF-8',
            'Authorization': 'Bearer ' + self.channel_access_token
        }

    def reply_message(self, reply_token: str, messages):
        if not isinstance(reply_token, str):
            raise TypeError('reply_token must be str')
        if not isinstance(messages, (list, tuple)):
            messages = [messages]

        data = {
            "replyToken": reply_token,
            "messages": [message.to_dict() for message in messages]
        }
        url = self.DEFAULT_API_ENDPOINT+'/v2/bot/message/reply'
        res = super().post(url, data=data, headers=self.headers)
        if res.status_code != 200:
            logging.error('From Line:'+res.text)


class TextSendMessage:
    def __init__(self, text: str):
        self.type = 'text'
        self.text = text

    def to_dict(self):
        return {
            'type': self.type,
            'text': self.text
        }
