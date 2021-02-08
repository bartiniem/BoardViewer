#  """
#  -----------------------------------------------------------------------
#  Designed and implemented by BartN
#  -----------------------------------------------------------------------
#  """

# IMPORTS
import os
from datetime import datetime

from flask import Flask, session, redirect, url_for, request, render_template

# DEFINITIONS
from datautils import DataUtils

CARDS_FILE = "data/cards.yaml"
VOTES_FILE = "data/votes.yaml"

# INIT
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'e5ac358c-f0bf-11e5-9e39-d3b532c10a28'


# ROUTES
@app.route('/', methods=['GET', 'POST'])
def index():
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # gen_cards = DataUtils().get_cards()
    # DataUtils().save_data_to_yaml(gen_cards, CARDS_FILE)
    cards = DataUtils().get_cards(CARDS_FILE)
    good_cards = [card for card in cards if card.get("type") in "good"]
    bad_cards = [card for card in cards if card.get("type") in "bad"]
    votes = DataUtils().load_yaml_data(VOTES_FILE)
    sum_cards = len(cards)
    return render_template('dashboard.html', title="BoardViewer", good_cards=good_cards, bad_cards=bad_cards,
                           last_update=last_update, votes=votes, sum_cards=sum_cards)


if __name__ == '__main__':
    app.run(debug=False, port=5002)
