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

    # return list of people the current user follows
    return dict(
        # COMPLETE: return here any signed URLs you need.
        current=get_user_email(),
        get_users_url=URL('get_users', signer=url_signer),
        add_player_url=URL('add_player', signer=url_signer),
        url_signer=url_signer
    )


@action('group_page', method=["GET", "POST"])
@action.uses('group_page.html', url_signer, db, session, auth.user, url_signer.verify())
def group_page():
    return dict(
        get_users_url=URL('get_users', signer=url_signer),
        add_player_url=URL('add_player', signer=url_signer),
        get_groups_url=URL('get_groups', signer=url_signer),
        create_group_url=URL('create_group', signer=url_signer),
        change_id_url=URL('change_id', signer=url_signer),
        delete_group_url=URL('delete_group', signer=url_signer),
        set_active_url=URL('set_active', signer=url_signer),
        url_signer=url_signer,
    )


@action('game_page', method=["GET", "POST"])
@action.uses('game_page.html', url_signer, db, session, auth.user, url_signer.verify())
def game_page():
    if request.method == 'POST':
        # Handle form submission and update player statistics
        group_id = int(request.json.get('group_id'))
        killed_player_id = int(request.json.get('killed_player_id'))
        current_assasin_id = int(request.json.get('current_assasin_id'))

        # Update killed player statistics
        killed_player_stats = db.statistics(player_id=killed_player_id)
        if killed_player_stats:
            killed_player_stats.update_record(
                kills=killed_player_stats.kills + 1)
        else:
            db.statistics.insert(player_id=killed_player_id,
                                 kills=1, games_survived=0)

        # Update current assassin statistics
        current_assasin_stats = db.statistics(player_id=current_assasin_id)
        if current_assasin_stats:
            current_assasin_stats.update_record(
                games_survived=current_assasin_stats.games_survived + 1)
        else:
            db.statistics.insert(
                player_id=current_assasin_id, kills=0, games_survived=1)

        # Update game status and winner in the group table
        db.group.update_or_insert(
            (db.group.id == group_id), winner=current_assasin_id, active=False)

        return dict(message="Player statistics updated")

    return dict(
        get_users_url=URL('get_users', signer=url_signer),
        get_groups_url=URL('get_groups', signer=url_signer),
        create_group_url=URL('create_group', signer=url_signer),
        change_id_url=URL('change_id', signer=url_signer),
        delete_group_url=URL('delete_group', signer=url_signer),
        vote_player_url=URL('vote_player', signer=url_signer),
        set_inactive_url=URL('set_inactive', signer=url_signer),
        url_signer=url_signer,
    )


@action('statistics_page', method=["GET", "POST"])
@action.uses('statistics_page.html', db, auth.user, url_signer.verify())
def statistics_page():
    if request.method == 'GET':
        # Retrieve statistics for all players
        players = db(db.player).select()
        statistics = []
        for player in players:
            player_statistics = db.statistics(player_id=player.id)
            if player_statistics:
                statistics.append({
                    'player': player,
                    'kills': player_statistics.kills,
                    'games_survived': player_statistics.games_survived
                })
            else:
                statistics.append({
                    'player': player,
                    'kills': 0,
                    'games_survived': 0
                })

        # Sort statistics by kills in descending order
        leaderboard = sorted(
            statistics, key=lambda s: s['kills'], reverse=True)

        return dict(statistics=statistics, leaderboard=leaderboard)

    elif request.method == 'POST':
        # Handle form submission and update player statistics
        player_id = int(request.forms.get('player_id'))
        kills = int(request.forms.get('kills'))
        games_survived = int(request.forms.get('games_survived'))

        # Update player statistics in the database
        db.statistics.update_or_insert(
            (db.statistics.player_id == player_id),
            player_id=player_id,
            kills=kills,
            games_survived=games_survived
        )

        # Redirect to the statistics page after updating
        redirect(URL('statistics_page', signer=url_signer))

    return dict(
        get_users_url=URL('get_users', signer=url_signer),
        add_player_url=URL('add_player', signer=url_signer),
        get_groups_url=URL('get_groups', signer=url_signer),
        create_group_url=URL('create_group', signer=url_signer),
        change_id_url=URL('change_id', signer=url_signer),
        delete_group_url=URL('delete_group', signer=url_signer),
        set_active_url=URL('set_active', signer=url_signer),
        url_signer=url_signer,
    )


# BACKEND FUNCTIONS
@action("get_users")
@action.uses(db, auth.user)
def get_users():
    # grabbing users
    rows = db(db.auth_user.username).select()
    players = db(db.player.nickname).select()
    current = get_user_email()
    currentUser = ""
    for i in rows:
        if (current == i.email):
            currentUser = i.username
    # GRABBING GROUP
    return dict(rows=rows, currentUser=currentUser, players=players)


@action("get_groups")
@action.uses(db, auth.user)
def get_groups():
    # grabbing users
    groups = db(db.group).select()
    return dict(groups=groups)


@action("create_group", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def create_group():
    creator = request.json.get('creator')
    current_assasin = request.json.get('current_assasin')
    winner = request.json.get('winner')
    players = request.json.get('players')
    id = db.group.insert(
        creator=creator,
        current_assasin=current_assasin,
        winner=winner,
        players=players,
    )

    return dict(id=id, message="added group successfully")


@action("change_id", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def change_id():
    id = request.json.get('id')

    currentUser = request.json.get('currentUser')
    player = db(db.player.username == currentUser).select().first()

    if player:
        # Update the group_id attribute of the player
        player.update_record(group_id=id)
        message = "Group ID updated successfully"
    else:
        message = "Player not found"
    return dict(id=id, message="added player successfully")


@action("add_player", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def add_player():
    username = request.json.get('username')
    nickname = request.json.get('nickname')
    id = db.player.insert(username=username, nickname=nickname)
    return dict(id=id, message="added player successfully")


@action('delete_group')
@action.uses(url_signer.verify(), db)
def delete_group():
    username = request.params.get('username')
    player = db(db.player.username == username).select().first()
    # grabbing all groups

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
    group_id = request.json.get('group_id')
    groups = db(db.group).select()
    players = db(db.player).select()
    temp = []
    current_assasin = None
    for p in players:
        if p.group_id == group_id:
            temp.append(p.username)

    if temp:
        current_assasin = random.choice(temp)

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
    group_id = request.json.get('group_id')
    groups = db(db.group).select()
    for g in groups:
        if g.id == group_id:
            g.update_record(active=False)
    print("INACTIVE SUCCESS")
    print(groups)
    return dict(message="inactive success")


@action("vote_player", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def vote_player():
    currentUser = request.json.get('currentUser')
    voted_player = request.json.get('voted_player')
    players = db(db.player).select()
    for p in players:
        if p.username == currentUser:
            p.update_record(vote=voted_player)

    return dict(message="voted_played succesfully")
