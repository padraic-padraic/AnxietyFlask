from celery.schedules import crontab
from random import random

WORK_DIR = '/Users/padraic/AnxietyFlask/AnxietyFlask/'
DOMAIN = 'your.domain'

class Config():
    DEBUG=False
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_TIMEZONE = 'Europe/London'
    CELERYBEAT_SCHEDULE = {
        'Email every now and again': {
            'task': 'tasks.send_mail',
            'schedule': crontab(hour='4, 9, 12, 16, 19, 22', minute='0')
            },
        'Get Mail': {
            'task': 'tasks.get_mail',
            'schedule': crontab(hour='3, 7, 9, 10, 11, 12, 14, 15, 17, 18, 21, 23', minute=30)
        }
    }
    ADMIN_MAIL = 'your_mail@isp.tld'
    ADMIN = 'You!'
    SECRET_KEY = 'A secret...'
    DOMAIN = 'Your.Domain'

class Testing(Config):
    DEBUG = True
    DOMAIN = 'localhost:5000'

class MailgunConfig(Config):
    API_KEY = 'MAILGUN_API_KEY'
    BASE_URL = 'https://api.mailgun.net/v2/'
    DOMAIN = 'YOUR_MAILGUN_DOMAIN'
    FROM = 'Your anxiety <email@example.com>'
