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
MAX_RETURNED_USERS = 20  # Our searches do not return more than 20 users.
MAX_RESULTS = 20  # Maximum number of returned meows.


@action('index')
@action.uses('index.html', db, auth.user, url_signer)
def index():

    # return list of backend URLs 
    return dict(
        # current is current user email 
        current=get_user_email(),
        get_users_url=URL('get_users', signer=url_signer), # URL for getting user list 
        add_player_url=URL('add_player', signer=url_signer), #URL for adding a new player
        url_signer=url_signer # url signer object
    )


@action('group_page', method=["GET", "POST"])
@action.uses('group_page.html', url_signer, db, session, auth.user, url_signer.verify())
def group_page():
    return dict(
        get_users_url=URL('get_users', signer=url_signer), # URL for getting user list
        add_player_url=URL('add_player', signer=url_signer), # URL for adding a new player 
        get_groups_url=URL('get_groups', signer=url_signer), # URL for getting group list 
        create_group_url=URL('create_group', signer=url_signer), # URL for creaitng new group 
        change_id_url=URL('change_id', signer=url_signer),  # URL for changing id 
        delete_group_url=URL('delete_group', signer=url_signer), # URL for deleting a group 
        set_active_url=URL('set_active', signer=url_signer), # URL for setting a group as active
        url_signer=url_signer, # URL signer object 
    )


@action('game_page', method=["GET", "POST"])
@action.uses('game_page.html', url_signer, db, session, auth.user, url_signer.verify())
def game_page():
    return dict(
        get_users_url=URL('get_users', signer=url_signer),
        get_groups_url=URL('get_groups', signer=url_signer),
        create_group_url=URL('create_group', signer=url_signer),
        change_id_url=URL('change_id', signer=url_signer),
        delete_group_url=URL('delete_group', signer=url_signer),
        vote_player_url=URL('vote_player', signer=url_signer),
        set_inactive_url=URL('set_inactive', signer=url_signer),
        add_win_url=URL('add_win', signer=url_signer),
        url_signer=url_signer,
    )


@action('statistics_page', method=["GET", "POST"])
@action.uses('statistics_page.html', db, auth.user, url_signer.verify())
def statistics_page():
    return dict(
        get_users_url=URL('get_users', signer=url_signer),
        get_groups_url=URL('get_groups', signer=url_signer),
        add_last_words_url=URL('add_last_words', signer=url_signer), # URL for posting new last_word for player 
        url_signer=url_signer,
    )

# BACKEND FUNCTIONS

@action("get_users")
@action.uses(db, auth.user)
def get_users():
    # grabbing users
    rows = db(db.auth_user.username).select() # Querying the database to get user rows
    players = db(db.player.nickname).select() # Querying databse to get player rows 
    current = get_user_email() # GEtting email of current user 
    currentUser = "" # will be filled with current user username 
    for i in rows:
        if (current == i.email):
            currentUser = i.username
    # returning all users, players, and current user username 
    return dict(rows=rows, currentUser=currentUser, players=players)


@action("get_groups")
@action.uses(db, auth.user)
def get_groups():
    # returning all groups in the database 
    groups = db(db.group).select()
    return dict(groups=groups)


@action("create_group", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def create_group():
    creator = request.json.get('creator') # grab creator for JSON request 
    current_assasin = request.json.get('current_assasin') # current_assasin from JSON REQUEST 
    winner = request.json.get('winner') # Winner from JSON request 
    players = request.json.get('players') # players from JSON request 
    # inserting the new group with posted data into databse 
    # id is return into the id variable when created 
    id = db.group.insert(
        creator=creator,
        current_assasin=current_assasin,
        winner=winner,
        players=players,
    )
    # id is useful later on when we use it to assign players to group ids 
    return dict(id=id, message="added group successfully")


@action("change_id", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def change_id():
    id = request.json.get('id')

    currentUser = request.json.get('currentUser')
    player = db(db.player.username == currentUser).select().first() # find player by username in database
    if player: # if player exists then update their record 
        # Update the group_id attribute of the player
        player.update_record(group_id=id)
        message = "Group ID updated successfully"
    else:
        message = "Player not found"
    return dict(id=id, message="added player successfully")


@action("add_player", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def add_player():
    username = request.json.get('username') # grabbing JSON requests for username and nickname 
    nickname = request.json.get('nickname')
    id = db.player.insert(username=username, nickname=nickname) # insert player into databse and grab id of player
    return dict(id=id, message="added player successfully")


@action('delete_group')
@action.uses(url_signer.verify(), db)
def delete_group():
    username = request.params.get('username')
    player = db(db.player.username == username).select().first()  # grab player by username 

    # we want all groups filtered by the creator and that are not of the same id 
    # this is because the user can only have one created group so we must delete all other groups 
    groups = db((db.group.creator == username) &
                (db.group.id != player.group_id)).select()

    for group in groups:
        # Fetch the specific group to delete
        group_to_delete = db.group(group.id)
        group_to_delete.delete_record()  # Delete the group
    return "ok"


@action("set_active", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def set_active():
    # setting a group active we get the id 
    group_id = request.json.get('group_id')
    groups = db(db.group).select()
    players = db(db.player).select()
    temp = []
    current_assasin = None
    for p in players:
        if p.group_id == group_id:
            temp.append(p.username)
    # since temp is filled with all users in the group we use it to pick an assasin at random 
    if temp:
        current_assasin = random.choice(temp)
    # setting group to be active and then returning it in the dictionary 
    active_group = None
    for g in groups:
        if g.id == group_id:
            # Update the group_id attribute of the player
            g.update_record(active=True)
            g.update_record(current_assasin=current_assasin)
            active_group = g
        else:
            g.update_record(active=False)
    return dict(active_group=active_group)


@action("set_inactive", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def set_inactive():
    # to set group as inactive we need the id 
    group_id = request.json.get('group_id')
    groups = db(db.group).select()
    for g in groups:
        if g.id == group_id:
            # set the record to be false if we find the matching id
            g.update_record(active=False)
    return dict(message="inactive success")


@action("vote_player", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def vote_player():
    # the player clicks on another player and we assign that clicked on player's id 
    # to be the value of the current user's vote field 
    currentUser = request.json.get('currentUser')
    voted_player = request.json.get('voted_player')
    players = db(db.player).select()
    for p in players:
        if (p.username == currentUser):
            p.update_record(vote=voted_player)

    return dict(message="voted_played succesfully")


@action("add_win", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def add_win():
    # when the assasin does not die we add a win 
    winner = request.json.get('winner')
    players = db(db.player).select()
    print("WINNNER")
    print(winner)
    for p in players:
        if p.username == winner:
            print("ADDDING win")
            if (p.wins == None): # if the wins are none, then we set it to 1 
                p.update_record(wins=1)
            else: # we add 1 to wins if they are alraedy an integer 
                p.update_record(wins=int(p.wins) + 1)
    return dict(message="winner gets another win")

@action("add_last_words", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def add_last_words():
    # this is for the stats page when the user wishes to update their last_words 
    currentUser = request.json.get('currentUser')
    last_words = request.json.get('last_words')
    player = db(db.player.username == currentUser).select().first()  # grab player by username 
    if(player):
        player.update_record(last_word=last_words)
    return dict(message="winner gets another win")





