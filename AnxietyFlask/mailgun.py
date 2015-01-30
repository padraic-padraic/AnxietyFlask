from config import MailgunConfig
from datetime import datetime, timedelta

from requests import get, post

conf = MailgunConfig()

class Mail():
    api_key =conf.API_KEY
    base_url = conf.BASE_URL
    domain = conf.DOMAIN

    def __init__(self, **kwargs):
        self.parameters = dict(kwargs.items())

    def add_params(self, **kwargs):
        for key, val in kwargs:
            self.parameters[key] = val

    def do_request(self, endpoint, r_type, **kwargs):
        if kargs:
            [self.parameters[key] = val for key, val in kwargs]
        if r_type == 'get:'
            _r = get(base_url+endpoint, params=self.parameters,
                              auth=('api',self.api_key))
        elif r_type == 'post':
            _r = post(base_url+endpoint, params=self.parameters,
                               auth=('api',self.api_key)
        else:
            raise Exception
        if _r.status_code != 200:
            raise Exception
        return _r.json()

class InMail(Mail):
    base_url = conf.BASE_URL + '/domains/'
    
    @classmethod
    def from_dict(_dict):
        self.parameters = dict(_dict.items())

    @classmethod
    def get_messages(cls):
        events = Mail(begin=datetime.now()-timedelta(days=1), end=datetime.now(),
                       pretty='no', event='stored').do_request('/events', 'get')
        messages = []
        for item in events['items']:
            data = cls().do_request('messages', 'get', key=item['sotrage']['key'])        
            messages.append(data)
            messages.append(InMail().from_dict(data))
        return messages

class OutMail(Mail):
    required = ['to', 'body', 'html', 'subject']

    def send(self):
        if not any(i in self.parameters.keys() for i in required):
            raise Exception
        self.do_request('messages', 'post')

