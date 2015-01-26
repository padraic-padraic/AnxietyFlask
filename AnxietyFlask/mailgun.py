from config import MailgunConfig

conf = MailgunConfig()

import requests

class Mail():
    api_key =conf.API_KEY
    base_url = conf.BASE_URL
    domain = conf.DOMAIN
    def __init__(self, **kwargs):
        self.parameters = dict(kwargs.items())

    def do_request(self, endpoint):
        _r = requests.get(base_url+endpoint, params=self.parameters, auth=('api',self.api_key))
        if _r.status_code != 200:
            raise Exception
        return _r.json()

class InMail(Mail):
    base_url = conf.BASE_URL + '/domains/'
    
    @classmethod:
    def get_messages(cls):

class OutMail(Mail):
    pass