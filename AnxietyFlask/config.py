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
    API_KEY = 'key-b0199c3faeb9e1a83f8a6eea519966c2'
    BASE_URL = 'https://api.mailgun.net/v2/'
    DOMAIN = 'https://mailgun.com/cp/domains/54c0f70e045ca436f8e9ccb3'
