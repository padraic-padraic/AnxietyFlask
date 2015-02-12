"""The email generating bot; this component is mostly a transcription of Paul's code, only used a little python to break the 
sentence fragments out into json files so I could add more / didn't have to transcrive them by hand"""
from AnxietyFlask.config import WORK_DIR
from random import choice, randint, sample

import json

FRAGMENTS = json.load(open(WORK_DIR+'fragments.json'))
PERSON = json.load(open(WORK_DIR+'person.json'))

def and_join(_list):
    return ', '.join(_list[:-1]) + ' and ' + _list[-1]

def monster():
    elements = PERSON.keys()
    _n = randint(2,3)
    return and_join([choice(PERSON[choice(elements)]) for i in xrange(_n)])

def capitalise(_str):
    _str = _str[:1].upper() + _str[1:]
    if _str[-1] != '.':
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
    return "\n"

def subject():
    return capitalise(randth('indicators') + ' ' + monster()).encode('ascii')

def compose(name, anxiety, reply):
    _str = "Dear " + name + ", \n"
    _str += capitalise(randth('contemplatives') + ' ' + anxiety)
    _str += "\n\n"
    _str += capitalise(randth('interrogatories') + ' ' + randth('offers')
                       + " \"" + anxiety + "\"-- " + randth('interrogatories'))
    _str += "\n" + quoth_the_bot(reply)
    _str += capitalise(randth('returns') + ' ' + randth('interrogatories')) + ' '
    _str += capitalise(randth('returns') + ' ' + randth('call-to-action'))
    return _str
