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
        follow_url=URL('set_follow', signer=url_signer),
        unfollow_url=URL('set_unfollow', signer=url_signer),
        meow_url=URL('add_meow', signer=url_signer),
    )

@action("get_users")
@action.uses(db, auth.user)
def get_users():
    # Implement. 
    rows = db(db.auth_user.username).select()    
    meows = db(db.meow.author >= 0).select()
    current = get_user_email()
    currentUser = "" 
    for i in rows: 
        if(current == i.email):
            currentUser = i.username
        
    # print(currentRow.email)    
    followList = db(db.follow.user_email == get_user_email()).select() 
    return dict(rows=rows, current=current, followList=followList, meows=meows, currentUser=currentUser)

@action("set_follow", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def set_follow():
    user_name = request.json.get('user_name')
    uid = request.json.get('uid') 
    # Check if the user_name already exists in the database
    existing_follow = db(db.follow.user_name == user_name).select().first()
    if existing_follow:
        # User_name already exists, return an appropriate response
        return dict(id=None, message="User already exists")
    # User_name doesn't exist, insert it into the database
    id = db.follow.insert(user_name=user_name, uid=uid)
    return dict(id=id, message="User added successfully")


@action('set_unfollow')
@action.uses(url_signer.verify(), db)
def set_unfollow():
    user_name = request.params.get('user_name')
    assert user_name is not None
    db(db.follow.user_name == user_name).delete() 
    return "ok"

@action('add_meow', method="POST")
@action.uses(db, auth.user, url_signer.verify())
def add_meow():
    user_name = request.json.get('user_name')
    content = request.json.get('content')
    ts = datetime.datetime.utcnow()
    reply_owner = request.json.get('reply_owner')
    total_replies = request.json.get('total_replies')
    # ts -= datetime.timedelta(seconds=random.uniform(60, 1000))
    db.meow.insert(
        author = user_name,
        timestamp = ts,
        content = content, 
        reply_owner = reply_owner,
        total_replies = total_replies,
    )
    return dict(ts=ts, message="added meow successfully", reply_owner=reply_owner, total_replies=total_replies)

# @action('edit_meow', method="POST")
# @action.uses(db, auth.user, url_signer.verify())
# def edit_meow
