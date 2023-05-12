import json
from .certify import Certification
import base64
import hashlib
import hmac
from .chat_gpt import ChatGPT
import logging
import traceback


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
    intents = {}

    def __init__(self, cert: Certification) -> None:
        if isinstance(cert, Certification):
            self.channel_secret = cert['Line']['channel_secret']
        else:
            raise TypeError('cert must be Certification object')

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

    def default(self):
        def decorator(func):
            self.intents['default'] = func
            return func
        return decorator

    @default
    def default_handler(self, event):
        logging.info(f'Default handler {event}')

    def handle(self, body, x_signature):
        """Handle webhook request from Line."""
        channel_secret = self.channel_secret

        # If fail to validate signature,will raise InvalidSignatureError
        if validate_signature(body, x_signature, channel_secret) != True:
            raise InvalidSignatureError(
                'Invalid signature. Please check your channel access token/channel secret.')

        body = json.loads(body)
        event = body['events'][0]

        try:
            message = event['message']['text']
            predict = ChatGPT.get_intent(message)
            self.intents[predict.intent](event, predict)
        except Exception:
            if event['type'] == 'follow':
                return
            func = self.intents.get('error')
            if func is not None:
                func(event, predict)
            else:
                logging.error('From handler:'+traceback.format_exc())
                self.intents['default'](event)
