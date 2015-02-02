from celery.schedules import crontab
from random import random
class Config():
    DEBUG=False
    SQLALCHEMY_DATABASE_URL = 'sqlite:///tmp/test.db'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_TIMEZONE = 'Europe/London'
    CELERYBEAT_SCHEDULE = {
        'Email every now and again': {
            'task': 'tasks.send_mail',
            'schedule': crontab(hour='0, 4, 7, 10, 11, 12, 13, 15, 16, 18, 19, 22'),
            'options': {'countdown': 3600*random(),
                        'link': 'tasks.error_mailer.s()'}
        },
        'Get Mail': {
            'task': 'tasks.get_mail'
            'schedule': crontab(hour='3, 7, 9, 10, 11, 12, 14, 15, 17, 18, 21, 23', minute=30)
        }
    }

class Testing(Config):
    DEBUG = True
    MAIL_DEBUG = True

class MailgunConfig(Config):
    API_KEY = 'key'
    BASE_URL = 'https://api.mailgun.net/v2/'
    DOMAIN = 'domain'
    FROM = 'Your email <email@example.com>'
