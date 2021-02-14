#  """
#  -----------------------------------------------------------------------
#  Designed and implemented by bartiniem
#  -----------------------------------------------------------------------
#  """

# IMPORTS
import os
from datetime import datetime
from flask import Flask, session, redirect, url_for, request, render_template

from datautils import DataUtils

# DEFINITIONS

# INIT
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'e5ac358c-f0bf-11e5-9e39-d3b532c10a28'
app.config['next_id'] = 100
app.config['last_show_id'] = 2


# ROUTES
@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('mainpage.html', title="BoardViewer")


@app.route('/', methods=['GET', 'POST'])
def index():
    username = get_username()
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cards = DataUtils().get_cards()
    good_cards = [card for card in cards if card.get("type") in "good"]
    bad_cards = [card for card in cards if card.get("type") in "bad"]
    votes = DataUtils().get_votes()
    sum_cards = len(cards)
    good_cards = DataUtils().update_user_data(good_cards)
    bad_cards = DataUtils().update_user_data(bad_cards)
    votes = DataUtils().update_votes_data(votes)
    print("usr: {}".format(username))
    return render_template('dashboard.html', title="BoardViewer", username=username,
                           good_cards=good_cards, bad_cards=bad_cards,
                           last_update=last_update, votes=votes, sum_cards=sum_cards,
                           last_show_id=app.config['last_show_id'])


@app.route('/preview', methods=['GET', 'POST'])
def preview():
    username = get_username()
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cards = DataUtils().get_cards()
    good_cards = [card for card in cards if card.get("type") in "good"]
    bad_cards = [card for card in cards if card.get("type") in "bad"]
    votes = DataUtils().get_votes()
    sum_cards = len(cards)
    good_cards = DataUtils().update_user_data(good_cards)
    bad_cards = DataUtils().update_user_data(bad_cards)
    votes = DataUtils().update_votes_data(votes)
    return render_template('preview.html', title="BoardViewer", username=username,
                           good_cards=good_cards, bad_cards=bad_cards,
                           last_update=last_update, votes=votes, sum_cards=sum_cards)


@app.route('/add_card', methods=['GET', 'POST'])
def add_card():
    username = get_username()
    app.config['next_id'] += 1
    message = add_card_form(app.config['next_id'])
    return render_template('add_card.html', title="Add card", username=username, message=message)


@app.route('/management/cards', methods=['GET', 'POST'])
def management_cards():
    username = get_username()
    cards = DataUtils().get_cards()
    return render_template('management_cards.html', title="Management cards", username=username, cards=cards)


@app.route('/management/card/<card_id>', methods=['GET', 'POST'])
def edit_card(card_id):
    username = get_username()
    message = edit_card_form(card_id)
    card = DataUtils().get_card_by_id(card_id)
    return render_template('edit_card.html', title="Edit card", username=username, card=card, message=message)


@app.route('/management/showcard/<card_id>', methods=['GET', 'POST'])
def show_card(card_id):
    username = get_username()
    cards = DataUtils().get_cards()
    for card in cards:
        if str(card.get("id")) == str(card_id):
            card["show"] = False if card.get("show") in [True] else True
    DataUtils().save_cards(cards)
    return redirect(url_for('management_cards'))


@app.route('/management/users', methods=['GET', 'POST'])
def management_users():
    username = get_username()
    users = DataUtils().get_users()
    return render_template('management_users.html', title="Management users", username=username, users=users)


@app.route('/user_management/configuration', methods=['GET', 'POST'])
def user_configuration():
    username = get_username()
    user = DataUtils().get_user_by_name(username)
    initials = DataUtils().get_user_initials(username)
    cards = DataUtils().get_cards()
    user_cards = [card for card in cards if card.get("author") == initials]
    return render_template('user_configuration.html', title="User configuration", username=username,
                           user=user, cards=user_cards)


@app.route('/user_management/showcard/<card_id>', methods=['GET', 'POST'])
def show_user_card(card_id):
    cards = DataUtils().get_cards()
    for card in cards:
        if str(card.get("id")) == str(card_id):
            card["show"] = False if card.get("show") in [True] else True
    DataUtils().save_cards(cards)
    return redirect(url_for('user_configuration'))


@app.route('/user_management/card/<card_id>', methods=['GET', 'POST'])
def edit_user_card(card_id):
    username = get_username()
    message = edit_card_form(card_id)
    card = DataUtils().get_card_by_id(card_id)
    return render_template('edit_user_card.html', title="Edit user card", username=username, card=card, message=message)


@app.route('/login', methods=['GET', 'POST'])
def login():
    username = get_username()
    if request.method == 'POST':
        if request.form.get("login_btn"):
            login_name = request.form.get("login_name") if request.form.get("login_name") else ""
            login_pass = request.form.get("login_pass") if request.form.get("login_pass") else ""
            session['username'] = login_name
            print("login: {}".format(login_name))
    if 'username' in session:
        return redirect(url_for('index'))
    else:
        return render_template('login.html', title="Login", username=username)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    session.pop('passwd', None)
    return redirect(url_for('login'))


def add_card_form(id_to_set):
    message = ""
    if request.method == 'POST':
        if request.form.get("add_card_btn"):
            card_author = request.form.get("card_author").upper() if request.form.get("card_author") else ""
            card_emotions = request.form.get("card_emotions").capitalize() if request.form.get("card_emotions") else ""
            card_text = request.form.get("card_text").capitalize() if request.form.get("card_text") else ""
            card_type = request.form.get("card_type") if request.form.get("card_type") else ""
            cards = DataUtils().get_cards()
            new_card = {"author": card_author, "emotions": card_emotions, "id": int(id_to_set), "name": card_text,
                        "points": "", "show": False, "type": card_type}
            cards.append(new_card)
            DataUtils().save_cards(cards)
            message = "New card added: {}".format(new_card)
            app.config['next_id'] += 1
    return message


def edit_card_form(card_id):
    message = ""
    if request.method == 'POST':
        if request.form.get("save_card_btn"):
            card_author = request.form.get("card_author").upper() if request.form.get("card_author") else ""
            card_emotions = request.form.get("card_emotions").capitalize() if request.form.get("card_emotions") else ""
            card_text = request.form.get("card_text").capitalize() if request.form.get("card_text") else ""
            card_type = request.form.get("card_type") if request.form.get("card_type") else ""
            card_show = request.form.get("card_show") if request.form.get("card_show") else False
            card_points = request.form.get("card_points") if request.form.get("card_points") else ""
            cards = DataUtils().get_cards()
            new_card = {"author": card_author, "emotions": card_emotions, "name": card_text, "show": bool(card_show),
                        "type": card_type}
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


if __name__ == '__main__':
    app.run(debug=False, port=5002)
