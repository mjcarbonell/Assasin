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
    Field('creator'), # represents the user who created the group 
    Field('current_assasin'), # Stores the username of the current_assasin of the group session 
    Field('winner'), # this can either be bystanders or the username of the assasin
    Field('players', 'list:string'), 
    Field('bot', 'boolean', default=False), # Indicates whether group is hosted by a bot
    Field('active', 'boolean', default=False), # INdicates active status of the group 
)
db.define_table(
    'player',
    Field('username'), # this is the username retrieved from auth.user 
    Field('nickname'), # this is the nickname that user must enter to register themselves as player 
    Field('group_id', 'reference group'), # group_id that must be assigned to an exisitng group
    Field('wins', 'integer', default=0), # total wins. A player wins if they were the assasin and did not get killed 
    Field('last_word'), # last_word is our form of a quote system. Like a bio on Discord 
    Field('vote', 'reference player'), # Vote field is the id of an exisiting player 
    Field('creation_date', 'datetime', default=get_time), 
)

db.define_table('statistics',
                Field('player_id', 'reference player'),
                Field('kills', 'integer', default=0),
                Field('games_survived', 'integer', default=0)
                )

def add_users_for_testing():  # Adding players and groups here
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