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


# Define your table below
#
# db.define_table('thing', Field('name'))
#
# always commit your models to avoid problems later

db.define_table(
    'player',
    Field('username'),
    Field('nickname'),
    Field('group_id'),
    Field('wins'),
    Field('last_word'),
    Field('user_email',  default=get_user_email),
    Field('creation_date', 'datetime', default=get_time),
)

db.define_table('statistics',
                Field('player_id', 'reference player'),
                Field('kills', 'integer', default=0),
                Field('games_survived', 'integer', default=0)
                )

db.define_table(
    'group',
    Field('author'),
    Field('content'),
    Field('reply_owner'),
    Field('total_replies'),
    Field('timestamp', 'datetime', default=get_time),
)


db.commit()

# Comment out this line if you are not interested.
