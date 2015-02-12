from celery import Celery, Task
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_wtf import CsrfProtect
from AnxietyFlask.config import Config
from AnxietyFlask.models import db

csrf = CsrfProtect()

def make_app():
    ## Initialise and set up the application
    app = Flask(__name__)
    #Change this
    app.config.from_object(Config)
    db.init_app(app)
    Bootstrap(app)
    csrf.init_app(app)
    return app

def make_celery_app(app=None):
    if app is None:
        app = make_app()
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery