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


@action("add_player", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def add_player():
    username = request.json.get('username')
    nickname = request.json.get('nickname')
    id = db.player.insert(username=username, nickname=nickname)
    return dict(id=id, message="added player successfully")


@action('group_page', method=["GET", "POST"])
@action.uses('group_page.html', url_signer, db, session, auth.user, url_signer.verify())
def group_page():

    return dict()


@action('statistics_page', method=["GET", "POST"])
@action.uses('statistics_page.html', db, auth.user, url_signer.verify())
def statistics_page():
    if request.method == 'GET':
        # Retrieve statistics for all players
        players = db(db.player).select()
        statistics = {}
        for player in players:
            player_statistics = db(
                db.statistics.player_id == player.id).select().first()
            if player_statistics:
                statistics[player.id] = {
                    'player': player,
                    'kills': player_statistics.kills,
                    'games_survived': player_statistics.games_survived
                }
            else:
                statistics[player.id] = {
                    'player': player,
                    'kills': 0,
                    'games_survived': 0
                }

        return dict(statistics=statistics, url_signer=url_signer)

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

        # Redirect back to the statistics page
        redirect(URL('statistics_page', signer=url_signer))
