import openai
from .certify import Certification
import json
# Entity Recognition Prompt
ER_PROMPT = """
Example:
<User> 馬鈴薯切掉發芽還可以吃嗎?
<Assistant> "intent":"Other Inquiries","entities":[]

<User> 我被詐騙了
<Assistant> "intent":"Other Inquiries","entities":[]

<User> 我想問蝦皮的詐騙是不是真的?
<Assistant> "intent":"Other Inquiries","entities":[]

<User> 這是假網站嗎?
<Assistant> "intent":"Inquire About Fraudulent URL","entities":[]

<User> 我感覺這個網站很可疑 https://www.google.com
<Assistant> "intent":"Inquire About Fraudulent URL","entities":["type":"URL","value":"https://www.google.com"]

Identify the following items from the message:
- Intent of the message
- Intent only can be "Inquire About Fraudulent TEL" or "Inquire About Fraudulent LineID" or "Inquire About Fraudulent URL" or "Other Inquiries" or "None"
- Entity only can be type of URL, TEL, LineID.
- Entities can be multiple.

The message is separated by three backticks. Format your response as a JSON Object with "query","intent" and "entities" as keys.
The "entities" value is a list that stores JSON Objects with "type" and "value" as keys.
If the entity does not exist, just use "[]" as the value for entities.
Keep your response as concise as possible.

<User>: ```{}```
<Assistant> ...
"""


class ChatGPT:
    DEFAULT_MODEL = "gpt-3.5-turbo"
    def __init__(self,cert) -> None:
        if isinstance(cert, Certification):
            openai.api_key = cert['OpenAI']['api_key']
    
    @staticmethod
    def get_intent(message, model="gpt-3.5-turbo"):
        if openai.api_key is None:
            raise ValueError("OpenAI API Key is not set")
        messages = [{"role": "user", "content": ER_PROMPT.format(message)}]
        
        data={
            'model': model,
            'messages': messages,
            'temperature': 0 # this is the degree of randomness of the model's output
        }
        response = openai.ChatCompletion.create(**data)

        predict = response.choices[0].message["content"]
        return Intent.new_from_dict(json.loads(predict))


    def create_completion(self,messages,model=DEFAULT_MODEL, temperature=0.7):
        if not isinstance(messages, (list, tuple)):
            messages = [messages]
        
        data = {
            'model': model,
            'messages': [message.to_dict() for message in messages],
            'temperature': temperature
        }

        response = openai.ChatCompletion.create(**data)
        return response.choices[0].message["content"]

class Intent:
    def __init__(self, query='',intent='None',entities=[]) -> None:
        self.query = query
        self.intent = intent
        self.entities = entities
    
    @staticmethod
    def new_from_dict(data):
        return Intent(**data)


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