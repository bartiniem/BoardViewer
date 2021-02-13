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
CARDS_FILE = "data/cards.yaml"
VOTES_FILE = "data/votes.yaml"

# INIT
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'e5ac358c-f0bf-11e5-9e39-d3b532c10a28'
app.config['next_id'] = 100
app.config['last_show_id'] = 2


# ROUTES
@app.route('/', methods=['GET', 'POST'])
def index():
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cards = DataUtils().get_cards(CARDS_FILE)
    good_cards = [card for card in cards if card.get("type") in "good"]
    bad_cards = [card for card in cards if card.get("type") in "bad"]
    votes = DataUtils().load_yaml_data(VOTES_FILE)
    sum_cards = len(cards)
    good_cards = DataUtils().update_user_data(good_cards)
    bad_cards = DataUtils().update_user_data(bad_cards)
    votes = DataUtils().update_votes_data(votes)
    return render_template('dashboard.html', title="BoardViewer", good_cards=good_cards, bad_cards=bad_cards,
                           last_update=last_update, votes=votes, sum_cards=sum_cards,
                           last_show_id=app.config['last_show_id'])


@app.route('/preview', methods=['GET', 'POST'])
def preview():
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cards = DataUtils().get_cards(CARDS_FILE)
    good_cards = [card for card in cards if card.get("type") in "good"]
    bad_cards = [card for card in cards if card.get("type") in "bad"]
    votes = DataUtils().load_yaml_data(VOTES_FILE)
    sum_cards = len(cards)
    good_cards = DataUtils().update_user_data(good_cards)
    bad_cards = DataUtils().update_user_data(bad_cards)
    votes = DataUtils().update_votes_data(votes)
    return render_template('preview.html', title="BoardViewer", good_cards=good_cards, bad_cards=bad_cards,
                           last_update=last_update, votes=votes, sum_cards=sum_cards)


@app.route('/add_card', methods=['GET', 'POST'])
def add_card():
    message = ""
    id_to_set = app.config['next_id']
    app.config['next_id'] += 1
    if request.method == 'POST':
        if request.form.get("add_card_btn"):
            card_author = request.form.get("card_author").upper() if request.form.get("card_author") else ""
            card_emotions = request.form.get("card_emotions").capitalize() if request.form.get("card_emotions") else ""
            card_text = request.form.get("card_text").capitalize() if request.form.get("card_text") else ""
            card_type = request.form.get("card_type") if request.form.get("card_type") else ""
            cards = DataUtils().get_cards(CARDS_FILE)
            new_card = {"author": card_author, "emotions": card_emotions, "id": int(id_to_set), "name": card_text,
                        "points": "", "show": False, "type": card_type}
            cards.append(new_card)
            DataUtils().save_data_to_yaml(cards, CARDS_FILE)
            message = "New card added: {}".format(new_card)

    return render_template('add_card.html', title="Add card", message=message)


@app.route('/management/cards', methods=['GET', 'POST'])
def management_cards():
    cards = DataUtils().get_cards(CARDS_FILE)
    return render_template('management_cards.html', title="Management cards", cards=cards)


@app.route('/management/card/<card_id>', methods=['GET', 'POST'])
def edit_card(card_id):
    message = ""
    if request.method == 'POST':
        if request.form.get("save_card_btn"):
            card_author = request.form.get("card_author").upper() if request.form.get("card_author") else ""
            card_emotions = request.form.get("card_emotions").capitalize() if request.form.get("card_emotions") else ""
            card_text = request.form.get("card_text").capitalize() if request.form.get("card_text") else ""
            card_type = request.form.get("card_type") if request.form.get("card_type") else ""
            card_show = request.form.get("card_show") if request.form.get("card_show") else False
            card_points = request.form.get("card_points") if request.form.get("card_points") else ""
            cards = DataUtils().get_cards(CARDS_FILE)
            new_card = {"author": card_author, "emotions": card_emotions, "id": int(card_id), "name": card_text,
                        "points": card_points, "show": bool(card_show), "type": card_type}
            for card in cards:
                if str(card.get("id")) == str(card_id):
                    card.update(new_card)
            DataUtils().save_data_to_yaml(cards, CARDS_FILE)
            message = "Saved card data: {}".format(new_card)
    card = DataUtils().get_card_by_id(CARDS_FILE, card_id)
    return render_template('edit_card.html', title="Edit card", card=card, message=message)


@app.route('/management/showcard/<card_id>', methods=['GET', 'POST'])
def show_card(card_id):
    cards = DataUtils().get_cards(CARDS_FILE)
    for card in cards:
        if str(card.get("id")) == str(card_id):
            card["show"] = False if card.get("show") in [True] else True
    DataUtils().save_data_to_yaml(cards, CARDS_FILE)
    return redirect(url_for('management_cards'))


@app.route('/management/users', methods=['GET', 'POST'])
def management_users():
    users = DataUtils().get_users()
    return render_template('management_users.html', title="Management users", users=users)


if __name__ == '__main__':
    app.run(debug=False, port=5002)
