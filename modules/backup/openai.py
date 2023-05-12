from ..base_api import BaseApi
from ..certify import Certification
import json

DEFAULT_API_ENDPOINT = 'https://api.openai.com/'


#! Deprecated class
class ChatGPT(BaseApi):
    DEFAULT_PATH = 'v1/chat/completions'
    DEFAULT_TIMEOUT = 120
    DEFAULT_MODEL = 'gpt-3.5-turbo'

    def __init__(self, cert, headers=None, callback=None, timeout=DEFAULT_TIMEOUT, model=DEFAULT_MODEL, endpoint=DEFAULT_API_ENDPOINT, default_prompt=None) -> None:
        url = endpoint+self.DEFAULT_PATH
        if isinstance(cert, Certification):
            self.api_key = cert['OpenAI']['api_key']
        else:
            raise TypeError('cert must be Certification object')

        if default_prompt is not None:
            try:
                self.prompt = json.load(open('./prompt.json'))
            except FileNotFoundError:
                if isinstance(default_prompt, dict):
                    self.prompt = default_prompt
                else:
                    raise TypeError('prompt must be dict or json file')

        self.model = model
        if headers is None:
            headers = {
                'Content-Type': 'application/json; charset=UTF-8',
                'Authorization': 'Bearer ' + self.api_key
            }

        super().__init__(url, headers, callback, timeout)

    def create_completion(self, messages, temperature=0):
        if not isinstance(messages, (list, tuple)):
            messages = [messages]

        data = {
            'model': self.model,
            'messages': [message.to_dict() for message in messages],
            'temperature': temperature
        }

        # self.callback = lambda x: x['choices'][0]['message']['content']
        self._post(data=data)

    def get_completion(self):
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
