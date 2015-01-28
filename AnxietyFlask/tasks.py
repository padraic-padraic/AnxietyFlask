from AnxietyFlask import anxieties
from AnxietyFlask.factory import make_celery_app
from random import random

celery = make_celery_app()

@celery.task
def random_delay(task):
    time = 3600 * random()
    task.apply_async(countdown = time)

@celery.task
def get_mail():
    pass

anxieties = celery.task(anxieties)

@celery.on_after_configure.connect
def setup_periodic_tasks(send, **kwargs):
    pass