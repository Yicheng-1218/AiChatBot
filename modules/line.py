from .base_api import BaseApi
from .certify import Certification


class LineBotApi(BaseApi):
    DEFAULT_API_ENDPOINT = 'https://api.line.me'
    DEFAULT_TIMEOUT = 10

    def __init__(self, cert, headers=None, callback=None, timeout=10) -> None:
        url = self.DEFAULT_API_ENDPOINT+'/v2/bot/message/reply'

        if isinstance(cert, Certification):
            self.channel_access_token = cert['Line']['channel_access_token']
        else:
            raise TypeError('cert must be Certification object')

        if headers is None:
            headers = {
                'Content-Type': 'application/json; charset=UTF-8',
                'Authorization': 'Bearer ' + self.channel_access_token
            }

        super().__init__(url, headers, callback, timeout)

    def reply_message(self, reply_token: str, messages):
        if not isinstance(reply_token, str):
            raise TypeError('reply_token must be str')
        if not isinstance(messages, (list, tuple)):
            messages = [messages]

        data = {
            "replyToken": reply_token,
            "messages": [message.to_dict() for message in messages]
        }

        self._post(data=data)


class TextSendMessage:
    def __init__(self, text: str):
        self.type = 'text'
        self.text = text

    def to_dict(self):
        return {
            'type': self.type,
            'text': self.text
        }
