"""The email generating bot; this component is mostly a transcription of Paul's code, only used a little python to break the 
sentence fragments out into json files so I could add more / didn't have to transcrive them by hand"""
from AnxietyFlask.config import WORK_DIR
from random import choice, randint, sample

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
    _n = randint(2,3)
    return and_join([choice(PERSON[choice(elements)]) for i in xrange(_n)])

def capitalise(_str):
    _str = _str[:1].upper() + _str[1:]
    if not _str[-1] in ['.', '!', '?']:
        _str += '.'
    return _str

def randth(_key):
    #Horrible thing that makes repeated phrases that bit less likely
    return choice(sample(FRAGMENTS[_key], randint(1, len(FRAGMENTS[_key]))))

def quoth_the_bot(reply):
    if reply:
        return capitalise(randth('youknow') + ' ' + randth('datespan')
                          + ' ' + randth('action') + ', ' + reply + '-- and '
                          + randth('youknow') + ' ' + randth('indicators')
                          + ' ' + monster()) + "\n"
    return ""

def subject():
    return capitalise(randth('indicators') + ' ' + monster()).encode('ascii')

EMAIL_TEMPLATE = """

Dear {0},

{1}

{2}

{3}
{4}

Sincerely, 

Your Anxiety
"""
HTML_TEMPLATE = """
Dear {0}, <br><br>
{1} <br>
{2} <br>
{3} <br>
{4} <br><br>
Sincerely, <br> Your Anxiety <br>
<a href="anxietylask.ddns.net/deactivate?uuid={uid}">Deactivate</a> or <a href="anxietyflask.ddns.net/delete?uuid={uid}">delete</a>
your account here.
"""

def compose(uid, name, anxiety, reply):
    question = capitalise(randth('contemplatives') + ' ' + anxiety)
    check_in = capitalise(randth('interrogatories') + ' ' + randth('offers')
                       + " \"" + anxiety + "\"-- " + randth('interrogatories'))
    quote = quoth_the_bot(reply)
    closer = capitalise(randth('returns') + ' ' + randth('interrogatories'))
    closer += capitalise(randth('returns') + ' ' + randth('call-to-action'))
    plain = EMAIL_TEMPLATE.format(name, question, check_in, quote, closer, uid=uid)
    html = HTML_TEMPLATE.format(name, question, check_in, quote, closer, uid=uid)
    return plain, html
