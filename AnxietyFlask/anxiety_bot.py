"""The email generating bot; this component is mostly a transcription of Paul's code, only used a little python to break the
sentence fragments out into json files so I could add more / didn't have to transcribe them by hand"""
from AnxietyFlask.config import WORK_DIR, DOMAIN
from AnxietyFlask.emails import ANXIETY_PLAIN, ANXIETY_HTML
from random import seed, choice, randint, sample

import json

FRAGMENTS = json.load(open(WORK_DIR+'fragments.json'))
PERSON = json.load(open(WORK_DIR+'person.json'))

def change_person(_str):
    _str = _str.replace(" I ", " you ")
    _str = _str.replace("my", "your")
    return _str

def uncapitalise(_str):
    return _str[:1].lower() + _str[1:]

def process(anxiety):
    return uncapitalise(change_person(anxiety))

def and_join(_list):
    return ', '.join(_list[:-1]) + ' and ' + _list[-1]

def monster():
    elements = PERSON.keys()
    _n = randint(1,2)
    return and_join([choice(PERSON[choice(elements)]) for i in xrange(_n)])

def capitalise(_str):
    _str = _str[:1].upper() + _str[1:]
    if not _str[-1] in ['.', '!', '?']:
        _str += '.'
    return _str

def randth(_key):
    return choice(FRAGMENTS[_key])

def quoth_the_bot(reply):
    youknow = sample(FRAGMENTS['youknow'],2)
    if reply:
        return capitalise(youknow.pop(0) + ' ' + randth('datespan')
                          + ' ' + randth('action') + ', ' + reply + '-- and '
                          + youknow.pop(0) + ' ' + randth('indicators')
                          + ' ' + monster()) + "\n"
    return ""

def subject():
    return capitalise(randth('indicators') + ' ' + monster())

def compose(uid, name, anxiety, reply = None):
    interrogatories = sample(FRAGMENTS['interrogatories'],3)
    returns = sample(FRAGMENTS['returns'],2)
    question = capitalise(randth('contemplatives') + ' ' + anxiety)
    check_in = capitalise(interrogatories.pop(0) + ' ' + randth('offers')
                       + " \"" + anxiety + "\"-- " + interrogatories.pop(0))
    quote = quoth_the_bot(reply)
    closer = capitalise(returns.pop(0) + ' ' + interrogatories.pop(0))
    closer += (' ' + capitalise(returns.pop(0) + ' ' + randth('call-to-action')))
    plain = ANXIETY_PLAIN.format(name, question, check_in, quote, closer, domain=DOMAIN, uid=uid)
    html = ANXIETY_HTML.format(name, question, check_in, quote, closer, domain = DOMAIN, uid=uid)
    return plain, html
