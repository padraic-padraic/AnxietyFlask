class Config():
    DEBUG=False
    SQLALCHEMY_DATABASE_URL = 'sqlite:///tmp/test.db'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_TIMEZONE = 'Europe/London'

class Testing(Config):
    DEBUG = True
    MAIL_DEBUG = True

class MailgunConfig(Config):
    API_KEY = 'key'
    BASE_URL = 'https://api.mailgun.net/v2/'
    DOMAIN = 'my.domain.com'
