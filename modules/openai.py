from .base_api import BaseApi
from .certify import Certification
import requests
import json

DEFAULT_API_ENDPOINT = 'https://api.openai.com/'


class ChatGPT(BaseApi):
    DEFAULT_PATH = 'v1/chat/completions'
    DEFAULT_TIMEOUT = 120
    DEFAULT_MODEL = 'gpt-3.5-turbo'

    def __init__(self, cert, headers=None, callback=None, timeout=DEFAULT_TIMEOUT, model=DEFAULT_MODEL, endpoint=DEFAULT_API_ENDPOINT, prompt=None) -> None:
        url = endpoint+self.DEFAULT_PATH
        if isinstance(cert, Certification):
            self.api_key = cert['OpenAI']['api_key']
        else:
            raise TypeError('cert must be Certification object')

        if prompt is not None:
            try:
                self.prompt = json.load(open('./prompt.json'))
            except FileNotFoundError:
                if isinstance(prompt, dict):
                    self.prompt = prompt
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
    url = json.load(open('./api_key.json'))['OpenAI']['DDIC_GPT']

    def __init__(self, prompt=None, callback=None) -> None:
        if prompt is not None:
            try:
                self.prompt = json.load(open('./prompt.json'))
            except FileNotFoundError:
                if isinstance(prompt, dict):
                    self.prompt = prompt
                else:
                    raise TypeError('prompt must be dict or json file')

        super().__init__(self.url, timeout=120, callback=callback)

    def send_messages(self, messages):
        if not isinstance(messages, (list, tuple)):
            messages = [messages]

        if self.prompt is not None:
            prompt = self.prompt['system']
            messages.insert(0, GptMessage('system', prompt))

        data = {
            "key": "0",
            "data": {
                "topic": "AI",
                "method": "ChatGPT",
                "data": {
                    "prompt": [msg.to_dict() for msg in messages]
                },
                "temperature": 0.7,
                "top_p": 1
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
    pass
