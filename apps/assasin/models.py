"""
This file defines the database models
"""

import datetime
import random
from py4web.utils.populate import FIRST_NAMES, LAST_NAMES, IUP
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_username():
    return auth.current_user.get('username') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later


db.define_table(
    'group',
    Field('creator'),
    Field('current_assasin'),
    Field('winner'), # this can either be bystanders or the username of the assasin
    Field('players', 'list:string'), 
)
db.define_table(
    'player',
    Field('username'),
    Field('nickname'),
    Field('group_id', 'reference group'),
    Field('wins'),
    Field('last_word'),
    Field('creation_date', 'datetime', default=get_time),
)

db.commit()

# Comment out this line if you are not interested. 