from AnxietyFlask import make_celery_app

celery = make_celery_app()

@celery.task
def get_mail():
    pass

@celery.task
def send_emails():
    pass


