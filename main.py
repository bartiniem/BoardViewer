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


# ROUTES
@app.route('/', methods=['GET', 'POST'])
def index():
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cards = DataUtils().get_cards(CARDS_FILE)
    good_cards = [card for card in cards if card.get("type") in "good"]
    bad_cards = [card for card in cards if card.get("type") in "bad"]
    votes = DataUtils().load_yaml_data(VOTES_FILE)
    sum_cards = len(cards)
    return render_template('dashboard.html', title="BoardViewer", good_cards=good_cards, bad_cards=bad_cards,
                           last_update=last_update, votes=votes, sum_cards=sum_cards)


@app.route('/preview', methods=['GET', 'POST'])
def preview():
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cards = DataUtils().get_cards(CARDS_FILE)
    good_cards = [card for card in cards if card.get("type") in "good"]
    bad_cards = [card for card in cards if card.get("type") in "bad"]
    votes = DataUtils().load_yaml_data(VOTES_FILE)
    sum_cards = len(cards)
    return render_template('preview.html', title="BoardViewer", good_cards=good_cards, bad_cards=bad_cards,
                           last_update=last_update, votes=votes, sum_cards=sum_cards)


@app.route('/add_card', methods=['GET', 'POST'])
def add_card():
    message = ""
    id_to_set = app.config['next_id']
    app.config['next_id'] += 1
    if request.method == 'POST':
        if request.form.get("add_card_btn"):
            card_author = request.form.get("card_author") if request.form.get("card_author") else ""
            card_emotions = request.form.get("card_emotions") if request.form.get("card_emotions") else ""
            card_text = request.form.get("card_text") if request.form.get("card_text") else ""
            card_type = request.form.get("card_type") if request.form.get("card_type") else ""
            cards = DataUtils().get_cards(CARDS_FILE)
            new_card = {"author": card_author, "emotions": card_emotions, "id": id_to_set, "name": card_text,
                        "points": "", "show": False, "type": card_type}
            cards.append(new_card)
            DataUtils().save_data_to_yaml(cards, CARDS_FILE)
            message = "New card added: {}".format(new_card)

    return render_template('add_card.html', title="Add card", message=message)


if __name__ == '__main__':
    app.run(debug=False, port=5002)
