import json
import traceback
import logging


class Certification:
    key = None

    def __init__(self, cert) -> None:
        if not isinstance(cert, str):
            raise TypeError('cert must be str to the path of json file')

        try:
            self.key = json.load(open(cert))
        except FileNotFoundError:
            raise FileNotFoundError('cert file not found')
        except TypeError:
            raise TypeError('cert file must be json file')
        except:
            logging.info(traceback.format_exc())
            raise Exception('unknown error')

    def __getitem__(self, key):
        return getattr(self, key)

    def __getattr__(self, name):
        if name in self.key:
            return self.key[name]
        else:
            raise AttributeError(f'Key {name} not found in cert file')

    def __dict__(self):
        return self.key


if __name__ == '__main__':
    c = Certification('api_key.json')
    print(c['Line'])
