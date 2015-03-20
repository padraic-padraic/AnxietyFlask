from AnxietyFlask.config import MailgunConfig
from datetime import datetime, timedelta
from email.utils import formatdate
from requests import get, post, delete
from time import mktime

CONF = MailgunConfig()

def rfc2822(dt):
    return formatdate(mktime(dt.timetuple()))

class Mail():
    """Base class for messages"""
    api_key = CONF.API_KEY
    base_url = CONF.BASE_URL
    domain = CONF.DOMAIN

    def __init__(self, **kwargs):
        self.parameters = dict(kwargs.items())

    def add_params(self, **kwargs):
        for key, val in kwargs:
            self.parameters[key] = val

    def do_request(self, endpoint, r_type, **kwargs):
        if kwargs:
            for key, val in kwargs:
                self.parameters[key] = val
        if r_type == 'get':
            _r = get(self.base_url+self.domain+endpoint, params=self.parameters,
                     auth=('api',self.api_key))
        elif r_type == 'post':
            _r = post(self.base_url+self.domain+endpoint, data=self.parameters,
                      auth=('api',self.api_key))
        elif r_type == 'delete':
            _r = delete(self.base_url+self.domain+endpoint, auth=('api', self.api_key))
        else:
            raise Exception
        if _r.status_code != 200:
            _r.raise_for_status()
        try:
            return _r.json()
        except ValueError:
            return True

class InMail(Mail):
    """Incoming messages, distinguished as fetching/deleting stored messages uses a slightly different base url"""
    base_url = CONF.BASE_URL + 'domains/'
    
    @classmethod
    def from_dict(cls,_dict):
        """Alternate factory, mostly for use by get_messages"""
        instance = cls()
        instance.parameters = dict(_dict.items())

    @classmethod
    def get_messages(cls):
        """Fetch the last days messages."""
        events = Mail(begin=rfc2822(datetime.now()-timedelta(days=1)), end=rfc2822(datetime.now()),
                       pretty='no', event='stored').do_request('events', 'get')
        messages = []
        for item in events['items']:
            data = Mail().do_request('messages/'+ item['storage']['key'], 'get')
            messages.append(cls().from_dict(data))
            cls().do_request('messages/' + item['sotrage']['key'], 'delete')
        return messages

class OutMail(Mail):
    """Outgoing messages. These can be constructed and sent in one shot e.g:
        OutMail(to='test@example.com', subject='Testing', text='1, 2, 3...').send() """
    required = ['to', 'text', 'subject']

    def send(self):
        if not any(i in self.parameters.keys() for i in self.required):
            raise Exception
        self.parameters['from'] = CONF.FROM
        self.do_request('messages', 'post')

