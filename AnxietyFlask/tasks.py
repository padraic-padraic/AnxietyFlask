from AnxietyFlask import anxieties, insert_reply
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

@celery.task(name='tasks.error_mailer')
def error_mailer(failed_users):
    if len(failed_users) == 0:
        return True
    body = "Dear" + celery.conf.ADMIN + "\n This is an email to let you know something went wrong (predictably).\n"
    body += "For you, a great many things have gone wrong, but that's neither here nor there: I'm talking"
    body += "about the website. Here's a list. \n"
    for failure, error in failed_users:
        body += "Account: " + failure.id + "\n"
        body += "Error Code: " + error + "\n"
        body += "To do something about it, click: " +  MANUAL_SEND_ENDPOINT + failure.uid
        body += "\n \n"
    body += 'Best wishes, \n Your Anxiety'
    OutMail(to=celer.conf.ADMIN_MAIL, subject = "More things you did wrong", text=body).send()

@celery.task(name='tasks.get_mail')
def get_mail():
    mail = InMail().get_messages()
    for message in mail:
        user = Account.query.filter_by(email=message.parameters['from']).first()
        if user is None:
            continue #Need to do more here
        else:
            insert_reply(user.id, mail.body)

@celery.task(name='tasks.send_mail')
def send_mail():
    status = anxieties()
    if isinstance(status, HttpError):
        raise TotalFailure("We're doomed, we're all doomed!")
    else:
        return status
