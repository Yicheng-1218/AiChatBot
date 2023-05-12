from ..base_api import BaseApi
from ..certify import Certification


#! Deprecated class
class LanguageUnderstanding(BaseApi):

    def __init__(self, cert, headers=None, callback=None, timeout=30, endpoint=None, intent_vault=0, project_name=None, deploy_name=None) -> None:
        if isinstance(cert, Certification):
            k = cert['AZURE']['CLU']
            self.api_key = k['api_key']
            self.endpoint = k['endpoint']
            self.deploy_name = k['deployment_name']
            self.project_name = k['project_name']
            self.intent_vault = k['intent_vault']
        else:
            raise TypeError('cert must be Certification object')
        self.timeout = timeout

        url = self.endpoint+'/language/:analyze-conversations?api-version=2022-10-01-preview'
        if headers is None:
            headers = {
                'Content-Type': 'application/json; charset=UTF-8',
                'Ocp-Apim-Subscription-Key': self.api_key
            }

        super().__init__(url, headers, callback, timeout)

    def analyze_message(self, message):
        """Analyze message to get intent

        Args:
            message (str): message to analyze

        Returns:
            class: Intent object.
        """
        data = {
            "kind": "Conversation",
            "analysisInput": {
                "conversationItem": {
                    "id": "1",
                    "participantId": "1",
                    "text": message
                }
            },
            "parameters": {
                "projectName": self.project_name,
                "deploymentName": self.deploy_name,
                "stringIndexType": "TextElement_V8"
            }
        }

        self._post(data=data)

        return Intent(self.data, self.intent_vault)


class Intent:
    def __init__(self, data, intent_vault=None) -> None:
        try:
            if not isinstance(data, dict):
                raise TypeError('data must be dict type')

            self.query = data['result']['query']
            prediction = data['result']['prediction']
            self.topIntent = prediction['topIntent'] \
                if prediction['intents'][0]['confidenceScore'] > intent_vault else 'None'
            self.intents = prediction['intents']
            self.entities = prediction['entities']
        except:
            self.query = None
            self.topIntent = None
            self.intents = None
            self.entities = None


if __name__ == '__main__':
    pass
