from AnxietyFlask import anxieties
from AnxietyFlask.factory import make_celery_app
from AnxietyFlask.mailgun import OutMail
from AnxietyFlask.models import Account
from random import random
from requests.exceptions import HttpError

class TotalFailure(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

celery = make_celery_app()

MANUAL_SEND_ENDPOINT = "http://path-to-site.com/api/send?uid="

def error_mailer(failed_users):
    body = "Dear Padraic, \n" + "This is an email to let you know something went wrong (predictably).\n"
           + "For you, a great many things have gone wrong, but that's neither here nor there: I'm talking" +
           "about the website. Here's a list. \n"
    for failure, error in failed_users:
        body += "Account: " + failure.id + "\n"
        body += "Error Code: " + error + "\n"
        body += "To do something about it, click: " +  MANUAL_SEND_ENDPOINT + failure.uid
        body += "\n \n"
    body += 'Best wishes, \n Your Anxiety'
    OutMail(to="admin@anxietyfla.sk", subject = "More things you did wrong", body=body).send()

@celery.task
def random_delay(task):
    time = 3600 * random()
    task.apply_async(countdown = time)

@celery.task
def get_mail():
    mail = InMail().get_messages()
    for message in mail:
        user = Account.query.filter_by(email=message.parameters['from']).first()
        if user is None:
            continue #Need to do more here
        else:
            insert_reply(user.id, mail.body)

@celery.task
def send_mail():
    status = anxieties()
    if isinstance(status, HttpError):
        raise TotalFailure("We're doomed, we're all doomed!")
    elif len(status) != 0:
        error_mailer(status)
    else:
        return True

@celery.on_after_configure.connect
def setup_periodic_tasks(task, **kwargs):
    pass