#  """
#  -----------------------------------------------------------------------
#  Designed and implemented by bartiniem
#  -----------------------------------------------------------------------
#  """

# GLOBAL IMPORTS
import os
from datetime import datetime
from flask import Flask, session, redirect, url_for, request, render_template

# LOCAL IMPORTS
from datautils import DataUtils

# DEFINITIONS

# INIT
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'e5ac358c-f0bf-11e5-9e39-d3b532c10a28'
app.config['next_id'] = 100
app.config['next_vote_id'] = 100
app.config['last_show_id'] = 2


# ROUTES
@app.route('/', methods=['GET', 'POST'])
def index():
    active_user = get_active_user()
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cards = DataUtils().get_cards()
    cards = DataUtils().update_points_emoji(cards)
    good_cards = [card for card in cards if card.get("type") in "good"]
    bad_cards = [card for card in cards if card.get("type") in "bad"]
    votes = DataUtils().get_votes()
    sum_cards = len(cards)
    good_cards = DataUtils().update_user_data(good_cards)
    bad_cards = DataUtils().update_user_data(bad_cards)
    votes = DataUtils().update_votes_data(votes)
    return render_template('dashboard.html', title="BoardViewer", active_user=active_user,
                           good_cards=good_cards, bad_cards=bad_cards, last_update=last_update, votes=votes,
                           sum_cards=sum_cards, last_show_id=app.config['last_show_id'])


@app.route('/preview', methods=['GET', 'POST'])
def preview():
    active_user = get_active_user()
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cards = DataUtils().get_cards()
    cards = DataUtils().update_points_emoji(cards)
    good_cards = [card for card in cards if card.get("type") in "good"]
    bad_cards = [card for card in cards if card.get("type") in "bad"]
    votes = DataUtils().get_votes()
    sum_cards = len(cards)
    good_cards = DataUtils().update_user_data(good_cards)
    bad_cards = DataUtils().update_user_data(bad_cards)
    votes = DataUtils().update_votes_data(votes)
    return render_template('preview.html', title="BoardViewer", active_user=active_user,
                           good_cards=good_cards, bad_cards=bad_cards, last_update=last_update, votes=votes,
                           sum_cards=sum_cards)


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


@app.route('/user_management/configuration', methods=['GET', 'POST'])
def user_configuration():
    username = get_username()
    active_user = get_active_user()
    if not active_user:
        return redirect(url_for('login'))
    cards = DataUtils().get_cards()
    votes = DataUtils().get_votes()
    user_cards = [card for card in cards if card.get("author") == username]
    user_votes = [vote for vote in votes if vote.get("author") == username]
    return render_template('/user_management/user_configuration.html', title="User configuration",
                           active_user=active_user, user=active_user, cards=user_cards, votes=user_votes)


@app.route('/user_management/showcard/<card_id>', methods=['GET', 'POST'])
def show_user_card(card_id):
    if not get_active_user():
        return redirect(url_for('login'))
    cards = DataUtils().get_cards()
    for card in cards:
        if str(card.get("id")) == str(card_id):
            card["show"] = False if card.get("show") in [True] else True
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get("login_btn"):
            login_name = request.form.get("login_name") if request.form.get("login_name") else ""
            login_pass = request.form.get("login_pass") if request.form.get("login_pass") else ""
            if DataUtils().get_user_by_name(login_name):
                session["username"] = login_name
    active_user = get_active_user()
    return render_template('login.html', title="Login", active_user=active_user)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    session.pop('passwd', None)
    return redirect(url_for('login'))


@app.route('/permission_denied', methods=['GET', 'POST'])
def permission_denied():
    active_user = get_active_user()
    return render_template('message_page.html', title="Permission denied.", message="Permission denied.",
                           active_user=active_user)


@app.errorhandler(404)
def not_found(error):
    active_user = get_active_user()
    return render_template('message_page.html', title="Page not found.", message="Something went wrong. 😢",
                           active_user=active_user)


def add_card_form(id_to_set):
    message = ""
    if request.method == 'POST':
        if request.form.get("add_card_btn"):
            active_user = get_active_user()
            card_emotions = request.form.get("card_emotions").capitalize() if request.form.get("card_emotions") else ""
            card_text = request.form.get("card_text").capitalize() if request.form.get("card_text") else ""
            card_type = request.form.get("card_type") if request.form.get("card_type") else ""
            cards = DataUtils().get_cards()
            new_card = {"author": active_user.get("name"), "emotions": card_emotions, "id": int(id_to_set),
                        "name": card_text, "points": "", "show": False, "type": card_type}
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
            new_vote = {"author": active_user.get("name"), "id": int(id_to_set), "value": vote_type, "show": False}
            votes.append(new_vote)
            DataUtils().save_votes(votes)
            message = "New vote added: {}".format(new_vote)
            app.config['next_vote_id'] += 1
    return message


def edit_card_form(card_id):
    message = ""
    if request.method == 'POST':
        if request.form.get("save_card_btn"):
            active_user = get_active_user()
            card_emotions = request.form.get("card_emotions").capitalize() if request.form.get("card_emotions") else ""
            card_text = request.form.get("card_text").capitalize() if request.form.get("card_text") else ""
            card_type = request.form.get("card_type") if request.form.get("card_type") else ""
            card_show = request.form.get("card_show") if request.form.get("card_show") else False
            card_points = request.form.get("card_points") if request.form.get("card_points") else ""
            cards = DataUtils().get_cards()
            new_card = {"author": active_user.get("name"), "emotions": card_emotions, "name": card_text,
                        "show": bool(card_show), "type": card_type}
            if card_points:
                new_card["points"] = card_points
            for card in cards:
                if str(card.get("id")) == str(card_id):
                    card.update(new_card)
            DataUtils().save_cards(cards)
            message = "Saved card data: {}".format(new_card)
    return message


def get_username():
    return session['username'] if 'username' in session else 'N/A'


def get_active_user():
    username = get_username()
    return DataUtils().get_user_by_name(username)


if __name__ == '__main__':
    app.run(debug=False, port=5002)
