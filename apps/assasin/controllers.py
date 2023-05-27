"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

import datetime
import random

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_username, get_user_email

url_signer = URLSigner(session)

# Some constants.
MAX_RETURNED_USERS = 20 # Our searches do not return more than 20 users.
MAX_RESULTS = 20 # Maximum number of returned meows. 

@action('index')
@action.uses('index.html', db, auth.user, url_signer)
def index():

    # return list of people the current user follows 
    return dict(
        # COMPLETE: return here any signed URLs you need.
        current=get_user_email(),
        get_users_url = URL('get_users', signer=url_signer),
        add_player_url = URL('add_player', signer=url_signer),
    )

@action("get_users")
@action.uses(db, auth.user)
def get_users():
    # grabbing users 
    rows = db(db.auth_user.username).select() 
    players = db(db.player.nickname).select()    
    current = get_user_email()
    currentUser = "" 
    for i in rows: 
        if(current == i.email):
            currentUser = i.username
    # GRABBING GROUP 
    return dict(rows=rows, currentUser=currentUser, players=players)

@action("add_player", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def add_player():
    username = request.json.get('username')
    nickname = request.json.get('nickname')
    id = db.player.insert(username=username, nickname=nickname)
    return dict(id=id, message="added player successfully")

# @action('edit_meow', method="POST")
# @action.uses(db, auth.user, url_signer.verify())
# def edit_meow
