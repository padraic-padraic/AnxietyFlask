class Config():
	DEBUG=False
	SQLALCHEMY_DATABASE_URL = 'sqlite:///tmp/test.db'
	MAIL_SERVER = 'localhost'
	MAIL_USE_SSL = True
	DEFAULT_MAIL_SENDER = 'your_anxiety@anxietyfla.sk'

class Testing(Config):
	DEBUG = True
	MAIL_DEBUG = True

class Mailgun_Config(Config):
    API_KEY = ''
    BASE_URL = ''