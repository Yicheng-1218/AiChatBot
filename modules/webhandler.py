import json
from .azure import LanguageUnderstanding, Intent
from .certify import Certification
import base64
import hashlib
import hmac


luis = None


class InvalidSignatureError(Exception):
    """Raised when signature validation fails."""


def validate_signature(body, x_signature: str, channel_secret: str):
    """Validate LINE request signature.

    Args:
        body (dict): Request body
        x_signature (str): X-Line-Signature header
        channel_secret (str): Message API Channel secret

    Raises:
        InvalidSignatureError: When validation fails
    """
    gen_signature = hmac.new(
        channel_secret.encode('utf-8'),
        body,
        hashlib.sha256
    ).digest()
    # Compare x-line-signature request header and the signature
    x_signature = x_signature.encode('utf-8')
    gen_signature = base64.b64encode(gen_signature)
    return hmac.compare_digest(x_signature, gen_signature)


class WebhookHandler:
    def __init__(self, cert) -> None:
        self.intents = {}

        if isinstance(cert, Certification):
            self._cert = cert
        else:
            raise TypeError('cert must be Certification object')
        global luis
        luis = LanguageUnderstanding(cert)

    def intent(self, intent):
        """Intent register decorator for the main function to handle.
            Adding intent to intents dict and initializing before the main function.
        Args:
            intent (str): intent name
        """
        def decorator(func):
            self.intents[intent] = func
            return func
        return decorator

    def handle(self, body, x_signature):
        """Handle webhook request from Line."""
        channel_secret = self._cert['Line']['channel_secret']

        # if fail to validate signature,will raise InvalidSignatureError
        if validate_signature(body, x_signature, channel_secret) != True:
            raise InvalidSignatureError(
                'Invalid signature. Please check your channel access token/channel secret.')

        body = json.loads(body)
        event = body['events'][0]
        message = event['message']['text']
        intent: Intent = luis.analyze_message(message)

        # intent = Intent.new_from_dict()
        if intent.topIntent in self.intents:

            self.intents[intent.topIntent](event, intent)
        else:
            raise ValueError(
                'No intent handler for intent: ' + intent.topIntent)
