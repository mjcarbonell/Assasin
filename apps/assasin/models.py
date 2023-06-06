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
    Field('bot', 'boolean', default=False),
    Field('active', 'boolean', default=False),
)
db.define_table(
    'player',
    Field('username'),
    Field('nickname'),
    Field('group_id', 'reference group'),
    Field('wins', 'integer', default=0),
    Field('last_word'),
    Field('vote', 'reference player'),
    Field('creation_date', 'datetime', default=get_time),
)

db.define_table('statistics',
                Field('player_id', 'reference player'),
                Field('kills', 'integer', default=0),
                Field('games_survived', 'integer', default=0)
                )

def add_users_for_testing(): 
    print("Adding user") 
    first_name = random.choice(FIRST_NAMES)
    last_name = first_name = random.choice(LAST_NAMES)
    group_id = db.group.insert(creator=first_name, bot=True)
    db.player.insert(username=first_name, nickname=last_name, group_id=group_id)
    for i in range(1): 
        db.player.insert(
            username=random.choice(FIRST_NAMES), 
            nickname=random.choice(LAST_NAMES), 
            group_id=group_id
        ) 


add_users_for_testing() 
add_users_for_testing()

db.commit()

# Comment out this line if you are not interested. 