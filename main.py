#  """
#  -----------------------------------------------------------------------
#  Designed and implemented by bartiniem
#  -----------------------------------------------------------------------
#  """

# GLOBAL IMPORTS
import argparse
import hashlib
import os
from datetime import datetime
from flask import Flask, session, redirect, url_for, request, render_template

# LOCAL IMPORTS
from settings import Settings
from datautils import DataUtils

# DEFINITIONS

# INIT
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'e5ac358c-f0bf-11e5-9e39-d3b532c10a28'
app.config['next_id'] = 100
app.config['next_vote_id'] = 100


# ROUTES
@app.route('/', methods=['GET', 'POST'])
def index():
    active_user = get_active_user()
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    settings = Settings().get_settings()
    show_points = settings.get("show_points")
    cards = DataUtils().get_cards()
    cards = DataUtils().update_points_emoji(cards)
    good_cards = [card for card in cards if card.get("type") in "good"]
    bad_cards = [card for card in cards if card.get("type") in "bad"]
    votes = DataUtils().get_votes()
    sum_cards = len(cards)
    sum_points = DataUtils().get_points_for_cards()
    good_cards = DataUtils().update_user_data(good_cards)
    bad_cards = DataUtils().update_user_data(bad_cards)
    votes = DataUtils().update_votes_data(votes)
    good_cards.sort(key=lambda c: c.get("last_edit"), reverse=False)
    bad_cards.sort(key=lambda c: c.get("last_edit"), reverse=False)
    votes.sort(key=lambda c: c.get("last_edit"), reverse=False)
    return render_template('dashboard.html', title="BoardViewer", active_user=active_user,
                           good_cards=good_cards, bad_cards=bad_cards, last_update=last_update, votes=votes,
                           sum_cards=sum_cards, sum_points=sum_points, show_votes=True, show_points=show_points)


@app.route('/cards/good/load', methods=['GET', 'POST'])
def cards_good_load():
    cards = DataUtils().get_cards()
    cards = DataUtils().update_points_emoji(cards)
    good_cards = [card for card in cards if card.get("type") in "good"]
    good_cards = DataUtils().update_user_data(good_cards)
    good_cards.sort(key=lambda c: c.get("last_edit"), reverse=False)
    return render_template('components/cards_box.html', cards=good_cards)


@app.route('/cards/bad/load', methods=['GET', 'POST'])
def cards_bad_load():
    cards = DataUtils().get_cards()
    cards = DataUtils().update_points_emoji(cards)
    bad_cards = [card for card in cards if card.get("type") in "bad"]
    bad_cards = DataUtils().update_user_data(bad_cards)
    bad_cards.sort(key=lambda c: c.get("last_edit"), reverse=False)
    return render_template('components/cards_box.html', cards=bad_cards)


@app.route('/preview', methods=['GET', 'POST'])
def preview():
    active_user = get_active_user()
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    settings = Settings().get_settings()
    show_points = settings.get("show_points")
    cards = DataUtils().get_cards()
    cards = DataUtils().update_points_emoji(cards)
    good_cards = [card for card in cards if card.get("type") in "good"]
    bad_cards = [card for card in cards if card.get("type") in "bad"]
    votes = DataUtils().get_votes()
    sum_cards = len(cards)
    sum_points = DataUtils().get_points_for_cards()
    good_cards = DataUtils().update_user_data(good_cards)
    bad_cards = DataUtils().update_user_data(bad_cards)
    votes = DataUtils().update_votes_data(votes)
    good_cards.sort(key=lambda c: c.get("last_edit"), reverse=False)
    bad_cards.sort(key=lambda c: c.get("last_edit"), reverse=False)
    votes.sort(key=lambda c: c.get("last_edit"), reverse=False)
    return render_template('preview.html', title="BoardViewer", active_user=active_user,
                           good_cards=good_cards, bad_cards=bad_cards, last_update=last_update, votes=votes,
                           sum_cards=sum_cards, sum_points=sum_points, show_votes=True, show_points=show_points)


@app.route('/add_card', methods=['GET', 'POST'])
def add_card():
    if not get_active_user():
        return redirect(url_for('login'))
    active_user = get_active_user()
    message = add_card_form(app.config['next_id'])
    message += vote_form(app.config['next_vote_id'])
    return render_template('add_card.html', title="Add card", active_user=active_user, message=message)


@app.route('/management/cards', methods=['GET', 'POST'])
def management_cards():
    active_user = get_active_user()
    if not active_user or active_user.get("role") != "admin":
        return redirect(url_for('permission_denied'))
    cards = DataUtils().get_cards()
    return render_template('/management/management_cards.html', title="Management cards", active_user=active_user,
                           cards=cards)


@app.route('/management/card/<card_id>', methods=['GET', 'POST'])
def edit_card(card_id):
    active_user = get_active_user()
    if not active_user or active_user.get("role") != "admin":
        return redirect(url_for('permission_denied'))
    message = edit_card_form(card_id)
    card = DataUtils().get_card_by_id(card_id)
    return render_template('/management/management_edit_card.html', title="Edit card", active_user=active_user,
                           card=card, message=message)


@app.route('/management/showcard/<card_id>', methods=['GET', 'POST'])
def show_card(card_id):
    active_user = get_active_user()
    if not active_user or active_user.get("role") != "admin":
        return redirect(url_for('permission_denied'))
    cards = DataUtils().get_cards()
    for card in cards:
        if str(card.get("id")) == str(card_id):
            card["show"] = False if card.get("show") in [True] else True
            card["last_edit"] = datetime.now().timestamp()
    DataUtils().save_cards(cards)
    return redirect(url_for('management_cards'))


@app.route('/management/show_vote/<vote_id>', methods=['GET', 'POST'])
def show_vote(vote_id):
    active_user = get_active_user()
    if not active_user or active_user.get("role") != "admin":
        return redirect(url_for('permission_denied'))
    votes = DataUtils().get_votes()
    for vote in votes:
        if str(vote.get("id")) == str(vote_id):
            vote["show"] = False if vote.get("show") in [True] else True
            vote["last_edit"] = datetime.now().timestamp()
    DataUtils().save_votes(votes)
    return redirect(url_for('management_cards'))


@app.route('/management/users', methods=['GET', 'POST'])
def management_users():
    active_user = get_active_user()
    if not active_user or active_user.get("role") != "admin":
        return redirect(url_for('permission_denied'))
    users = DataUtils().get_users()
    return render_template('/management/management_users.html', title="Management users", active_user=active_user,
                           users=users)


@app.route('/management/user/<user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    active_user = get_active_user()
    if not active_user or active_user.get("role") not in ["admin"]:
        return redirect(url_for('permission_denied'))
    message = edit_user_form(user_id)
    user = DataUtils().get_user_by_id(user_id)
    return render_template('/management/management_edit_user.html', title="Edit user", active_user=active_user,
                           user=user, message=message)


@app.route('/user_management/configuration', methods=['GET', 'POST'])
def user_configuration():
    username = get_username()
    active_user = get_active_user()
    if not active_user:
        return redirect(url_for('login'))
    cards = DataUtils().get_cards()
    votes = DataUtils().get_votes()
    points = DataUtils().get_points()
    user_cards = [card for card in cards if card.get("author") == username]
    user_votes = [vote for vote in votes if vote.get("author") == username]
    user_points = [point_row for point_row in points if point_row.get("author") == username]
    for user_p in user_points:
        user_p["name_6"] = DataUtils().get_card_by_id(user_p["points_6"])["name"]
        user_p["name_3"] = DataUtils().get_card_by_id(user_p["points_3"])["name"]
        user_p["name_1"] = DataUtils().get_card_by_id(user_p["points_1"])["name"]
    return render_template('/user_management/user_configuration.html', title="User configuration",
                           active_user=active_user, user=active_user, cards=user_cards, votes=user_votes,
                           points=user_points)


@app.route('/user_management/showcard/<card_id>', methods=['GET', 'POST'])
def show_user_card(card_id):
    if not get_active_user():
        return redirect(url_for('login'))
    cards = DataUtils().get_cards()
    for card in cards:
        if str(card.get("id")) == str(card_id):
            card["show"] = False if card.get("show") in [True] else True
            card["last_edit"] = datetime.now().timestamp()
    DataUtils().save_cards(cards)
    return redirect(url_for('user_configuration'))


@app.route('/user_management/show_vote/<vote_id>', methods=['GET', 'POST'])
def show_user_vote(vote_id):
    if not get_active_user():
        return redirect(url_for('login'))
    votes = DataUtils().get_votes()
    for vote in votes:
        if str(vote.get("id")) == str(vote_id):
            vote["show"] = False if vote.get("show") in [True] else True
            vote["last_edit"] = datetime.now().timestamp()
    DataUtils().save_votes(votes)
    return redirect(url_for('user_configuration'))


@app.route('/user_management/card/<card_id>', methods=['GET', 'POST'])
def edit_user_card(card_id):
    active_user = get_active_user()
    if not active_user:
        return redirect(url_for('login'))
    message = edit_card_form(card_id)
    card = DataUtils().get_card_by_id(card_id)
    return render_template('/user_management/user_edit_card.html', title="Edit user card", active_user=active_user,
                           card=card, message=message)


@app.route('/user_management/user/<user_id>', methods=['GET', 'POST'])
def user_edit_user_card(user_id):
    active_user = get_active_user()
    if not active_user or str(active_user.get("id")) != user_id:
        return redirect(url_for('permission_denied'))
    message = edit_user_form_from_user(user_id)
    user = DataUtils().get_user_by_id(user_id)
    return render_template('/user_management/user_edit_user.html', title="Edit user", active_user=active_user,
                           user=user, message=message)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get("login_btn"):
            login_name = request.form.get("login_name") if request.form.get("login_name") else ""
            login_pass = request.form.get("login_pass") if request.form.get("login_pass") else ""
            user = DataUtils().get_user_by_name(login_name)
            if user and str(hashlib.md5(login_pass.encode("utf-8")).hexdigest()) == user.get("passwd"):
                session["bv_username"] = login_name
    active_user = get_active_user()
    if active_user:
        return redirect(url_for('index'))
    return render_template('login.html', title="Login", active_user=active_user)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('bv_username', None)
    session.pop('bv_passwd', None)
    return redirect(url_for('login'))


@app.route('/permission_denied', methods=['GET', 'POST'])
def permission_denied():
    active_user = get_active_user()
    return render_template('message_page.html', title="Permission denied.", message="Permission denied.",
                           active_user=active_user)


@app.route('/goals', methods=['GET', 'POST'])
def goals():
    active_user = get_active_user()
    message = ""
    settings = Settings().get_settings()
    show_goals = settings.get("show_goals")
    cards = DataUtils().get_cards()
    filtered_cards = DataUtils().get_visible_cards()
    filtered_cards.sort(key=lambda c: c.get("points_sum"), reverse=True)
    if request.method == 'POST':
        if request.form.get("save_goals"):
            for card in filtered_cards:
                if request.form.get("goals_{}".format(card.get("id"))):
                    card["goals"] = request.form.get("goals_{}".format(card.get("id")))
                    message = "Data saved."
        DataUtils().save_cards(cards)
    return render_template('/goals.html', title="Goals", cards=filtered_cards[:5], active_user=active_user,
                           message=message, show_goals=show_goals)


@app.route('/vote', methods=['GET', 'POST'])
def vote():
    active_user = get_active_user()
    if not active_user:
        return redirect(url_for('login'))
    message = ""
    settings = Settings().get_settings()
    show_voting = settings.get("show_voting")
    filtered_cards = []
    already_voted = False
    points = DataUtils().get_points()
    users_voted = [elem.get("author") for elem in points]
    if active_user.get("name") in users_voted:
        message = "You have already voted."
        already_voted = True
    else:
        if request.method == 'POST':
            if request.form.get("vote_btn"):
                id_6 = int(request.form.get("points_6"))
                id_3 = int(request.form.get("points_3"))
                id_1 = int(request.form.get("points_1"))
                if len({id_6, id_3, id_1}) < len([id_6, id_3, id_1]):
                    message = "Duplicated cards. The Vote was canceled."
                else:
                    message = add_votes(id_6, id_3, id_1, active_user)
                    already_voted = True
        filtered_cards = DataUtils().get_visible_cards()
        filtered_cards.sort(key=lambda c: c.get("id"), reverse=False)
    return render_template('/vote.html', title="Vote", cards=filtered_cards, active_user=active_user, message=message,
                           already_voted=already_voted, show_voting=show_voting)


@app.route('/management/settings', methods=['GET', 'POST'])
def settings():
    active_user = get_active_user()
    if not active_user:
        return redirect(url_for('login'))

    settings_data = Settings().get_settings()
    return render_template('settings.html', title="settings", active_user=active_user,
                           settings=settings_data)


@app.route('/management/settings/set/<name>', methods=['GET', 'POST'])
def settings_set(name):
    active_user = get_active_user()
    if not active_user:
        return redirect(url_for('login'))

    Settings().set_new_value(name)
    return redirect(url_for('settings'))


def add_votes(id_6, id_3, id_1, active_user):
    cards = DataUtils().get_cards()
    points = DataUtils().get_points()
    for card in cards:
        if card.get("id") == id_6:
            card["points"] += ",6" if card["points"] else "6"
        if card.get("id") == id_3:
            card["points"] += ",3" if card["points"] else "3"
        if card.get("id") == id_1:
            card["points"] += ",1" if card["points"] else "1"
    new_points = {"author": active_user.get("name"), "points_6": id_6, "points_3": id_3, "points_1": id_1}
    points.append(new_points)
    DataUtils().save_points(points)
    DataUtils().save_cards(cards)
    message = "Thank you for votes. 6 -> #{} | 3 -> #{} | 1 -> #{}".format(id_6, id_3, id_1)
    return message


# [ERRORS]
@app.errorhandler(404)
def not_found(error):
    active_user = get_active_user()
    return render_template('message_page.html', title="Page not found.", message="Something went wrong. 😢",
                           active_user=active_user)


# [LOCAL]
def add_card_form(id_to_set):
    message = ""
    if request.method == 'POST':
        if request.form.get("add_card_btn"):
            active_user = get_active_user()
            card_emotions = request.form.get("card_emotions").capitalize() if request.form.get("card_emotions") else ""
            card_text = request.form.get("card_text") if request.form.get("card_text") else ""
            card_type = request.form.get("card_type") if request.form.get("card_type") else ""
            cards = DataUtils().get_cards()
            new_card = {"author": active_user.get("name"), "emotions": card_emotions, "id": int(id_to_set),
                        "name": card_text, "points": "", "show": False, "type": card_type, "last_edit": 0}
            cards.append(new_card)
            DataUtils().save_cards(cards)
            message = "New card added: {}".format(new_card)
            app.config['next_id'] += 1
    return message


def vote_form(id_to_set):
    message = ""
    if request.method == 'POST':
        if request.form.get("vote_btn"):
            active_user = get_active_user()
            vote_type = request.form.get("vote_type").upper() if request.form.get("vote_type") else ""
            votes = DataUtils().get_votes()
            new_vote = {"author": active_user.get("name"), "id": int(id_to_set), "value": vote_type, "show": False,
                        "last_edit": 0}
            votes.append(new_vote)
            DataUtils().save_votes(votes)
            message = "New vote added: {}".format(new_vote)
            app.config['next_vote_id'] += 1
    return message


def edit_card_form(card_id):
    message = ""
    if request.method == 'POST':
        if request.form.get("save_card_btn"):
            card_emotions = request.form.get("card_emotions").capitalize() if request.form.get("card_emotions") else ""
            card_text = request.form.get("card_text") if request.form.get("card_text") else ""
            card_type = request.form.get("card_type") if request.form.get("card_type") else ""
            card_show = request.form.get("card_show") if request.form.get("card_show") == "True" else False
            card_points = request.form.get("card_points") if request.form.get("card_points") else ""
            cards = DataUtils().get_cards()
            new_card = {"emotions": card_emotions, "name": card_text, "show": bool(card_show), "type": card_type}
            if card_points:
                new_card["points"] = card_points
            for card in cards:
                if str(card.get("id")) == str(card_id):
                    card.update(new_card)
            DataUtils().save_cards(cards)
            message = "Saved card data: {}".format(new_card)
    return message


def edit_user_form_from_user(user_id):
    message = ""
    if request.method == 'POST':
        if request.form.get("save_user_btn"):
            user_icon = request.form.get("user_icon") if request.form.get("user_icon") else ""
            user_color = request.form.get("user_color") if request.form.get("user_color") else ""
            user_card_color = request.form.get("user_card_color") if request.form.get("user_card_color") else ""
            users = DataUtils().get_users()
            new_user_data = {"icon": user_icon, "color": user_color, "card_color": user_card_color}
            for user in users:
                if str(user.get("id")) == str(user_id):
                    user.update(new_user_data)
            DataUtils().save_users(users)
            message = "Saved user data: {}".format(new_user_data)
    return message


def edit_user_form(user_id):
    message = ""
    if request.method == 'POST':
        if request.form.get("save_user_btn"):
            user_initials = request.form.get("user_initials") if request.form.get("user_initials") else ""
            user_name = request.form.get("user_name") if request.form.get("user_name") else ""
            user_icon = request.form.get("user_icon") if request.form.get("user_icon") else ""
            user_color = request.form.get("user_color") if request.form.get("user_color") else ""
            user_card_color = request.form.get("user_card_color") if request.form.get("user_card_color") else ""
            active_user = get_active_user()
            if active_user.get("role") in ["admin"]:
                user_role = request.form.get("user_role") if request.form.get("user_role") else "user"
            else:
                user_role = active_user.get("role")
            users = DataUtils().get_users()
            new_user_data = {"initials": user_initials, "name": user_name, "icon": user_icon, "color": user_color,
                             "card_color": user_card_color, "role": user_role}
            for user in users:
                if str(user.get("id")) == str(user_id):
                    user.update(new_user_data)
            DataUtils().save_users(users)
            message = "Saved user data: {}".format(new_user_data)
    return message


def get_username():
    return session['bv_username'] if 'bv_username' in session else 'N/A'


def get_active_user():
    username = get_username()
    return DataUtils().get_user_by_name(username)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--local', action='store_true', help="shows output")
    args = parser.parse_args()
    if args.local:
        app.run(debug=False, port=5002)
    else:
        app.run(debug=False, port=5002, host="0.0.0.0")

