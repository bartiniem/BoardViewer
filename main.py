#  """
#  -----------------------------------------------------------------------
#  Designed and implemented by bartiniem
#  -----------------------------------------------------------------------
#  """

# GLOBAL IMPORTS
import argparse
import datetime
import hashlib
import os
from flask import Flask, session, redirect, url_for, request, render_template

# LOCAL IMPORTS
from utils.settings import Settings
from utils.datautils import DataUtils

# DEFINITIONS

# INIT
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'e5ac358c-f0bf-11e5-9e39-d3b532c10a28'


# ROUTES
@app.route('/', methods=['GET', 'POST'])
def index():
    active_user = get_active_user()
    return render_template('dashboard.html', title="BoardViewer", active_user=active_user)


@app.route('/preview', methods=['GET', 'POST'])
def preview():
    active_user = get_active_user()
    return render_template('preview.html', title="BoardViewer", active_user=active_user)


@app.route('/votes/load', methods=['GET', 'POST'])
def votes_load():
    stats = DataUtils().get_stats()
    votes = DataUtils().get_votes_with_users(sort_by_last_edit=True, only_visible=True)
    return render_template('components/dashboard_points.html', votes=votes, stats=stats)


@app.route('/cards/<card_type>/load', methods=['GET', 'POST'])
def cards_positive_load(card_type):
    cards = DataUtils().get_cards_by_type(card_type, True)
    params = {
        'show_points': Settings().get_specific_setting("show_points")
    }
    return render_template('components/cards_box.html', cards=cards, params=params)


@app.route('/cards/add_card', methods=['GET', 'POST'])
def cards_add_card():
    active_user = get_active_user()
    if not active_user:
        return redirect(url_for('permission_denied'))

    card_text = request.args.get('card_text')
    card_emotions = request.args.get('card_emotions')
    card_type = request.args.get('card_type')
    new_card = {"author": active_user.get("name"), "emotions": card_emotions, "name": card_text, "type": card_type}
    message = DataUtils().add_card(new_card)
    return message


@app.route('/cards/vote', methods=['GET', 'POST'])
def cards_vote():
    active_user = get_active_user()
    if not active_user:
        return redirect(url_for('permission_denied'))

    vote_type = request.args.get("vote_type", "").upper()
    new_vote = {"author": active_user.get("name"), "value": vote_type}
    message = DataUtils().add_vote(new_vote)
    return message


@app.route('/add_card', methods=['GET', 'POST'])
def add_card():
    active_user = get_active_user()
    if not active_user:
        return redirect(url_for('login'))

    return render_template('add_card.html', title="Add card", active_user=active_user)


@app.route('/user/cards/<card_id>/save_new_data', methods=['GET', 'POST'])
def user_card_save_new_data(card_id):
    active_user = get_active_user()
    if not active_user:
        return redirect(url_for('permission_denied'))

    card_emotions = request.args.get("card_emotions").capitalize() if request.args.get("card_emotions") else ""
    card_text = request.args.get("card_text") if request.args.get("card_text") else ""
    card_type = request.args.get("card_type") if request.args.get("card_type") else ""
    new_card = {"emotions": card_emotions, "name": card_text, "type": card_type}
    message = DataUtils().edit_card_data(card_id, new_card)
    return message


@app.route('/cards/card/<card_id>/get_modal', methods=['GET', 'POST'])
def get_card_modal(card_id):
    card_data = DataUtils().get_card_by_id(card_id)
    return render_template('components/basic_modal.html', card_data=card_data)


@app.route('/user_management/configuration', methods=['GET', 'POST'])
def user_configuration():
    active_user = get_active_user()
    if not active_user:
        return redirect(url_for('login'))

    cards = DataUtils().get_cards()
    votes = DataUtils().get_votes()
    points = DataUtils().get_points()
    user_cards = [card for card in cards if card.get("author") == active_user.get('name')]
    user_votes = [vote for vote in votes if vote.get("author") == active_user.get('name')]
    user_points = [point_row for point_row in points if point_row.get("author") == active_user.get('name')]
    for user_p in user_points:
        user_p["name_6"] = DataUtils().get_card_by_id(user_p["points_6"])["name"]
        user_p["name_3"] = DataUtils().get_card_by_id(user_p["points_3"])["name"]
        user_p["name_1"] = DataUtils().get_card_by_id(user_p["points_1"])["name"]
    return render_template('/user_management/user_configuration.html', title="User configuration",
                           active_user=active_user, user=active_user, cards=user_cards, votes=user_votes,
                           points=user_points)


@app.route('/cards/card/<card_id>/showcard', methods=['GET', 'POST'])
def cards_card_showcard(card_id):
    active_user = get_active_user()
    if not active_user:
        return redirect(url_for('permission_denied'))

    card = DataUtils().get_card_by_id(card_id)
    if active_user.get("role") == "admin" or card.get('author') == active_user.get('name'):
        new_status = DataUtils().show_hide_card(card_id)
        icon = "green check circle" if new_status else "red times circle"
    else:
        icon = "yellow exclamation triangle"
    return f'️<i class="{icon} icon"></i>'


@app.route('/user_management/show_vote/<vote_id>', methods=['GET', 'POST'])
def show_user_vote(vote_id):
    if not get_active_user():
        return redirect(url_for('login'))

    DataUtils().vote_show_hide(vote_id)
    return redirect(url_for('user_configuration'))


@app.route('/cards/card/<card_id>/edit', methods=['GET', 'POST'])
def edit_user_card(card_id):
    active_user = get_active_user()
    if not active_user:
        return redirect(url_for('login'))

    card = DataUtils().get_card_by_id(card_id)
    if active_user.get("role") == "admin":
        return render_template('/management/management_edit_card.html', title="Edit admin card",
                               active_user=active_user, card=card)
    elif card.get('author') == active_user.get('name'):
        return render_template('/user_management/user_edit_card.html', title="Edit user card",
                               active_user=active_user, card=card)

    return render_template('message_page.html', title="Permission denied.", message="Permission denied.",
                           active_user=active_user)


@app.route('/user_management/user/<user_id>', methods=['GET', 'POST'])
def user_edit_user_card(user_id):
    active_user = get_active_user()
    if not active_user or str(active_user.get("id")) != user_id:
        return redirect(url_for('permission_denied'))

    user = DataUtils().get_user_by_id(user_id)
    return render_template('/user_management/user_edit_user.html', title="Edit user", active_user=active_user,
                           user=user)


@app.route('/user_management/user/<user_id>/save_new_data', methods=['GET', 'POST'])
def user_edit_user_card_save_new_data(user_id):
    active_user = get_active_user()
    if not active_user or str(active_user.get("id")) != user_id:
        return redirect(url_for('permission_denied'))

    new_user_data = {
        "icon": request.args.get("user_icon"),
        "color": request.args.get("user_color"),
        "card_color": request.args.get("user_card_color")
    }
    return DataUtils().update_user_data(user_id, new_user_data)


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
    show_goals = Settings().get_specific_setting("show_goals")
    filtered_cards = DataUtils().get_visible_cards()
    filtered_cards.sort(key=lambda c: c.get("points_sum"), reverse=True)
    return render_template('/goals.html', title="Goals", active_user=active_user,
                           cards=filtered_cards[:6], show_goals=show_goals)


@app.route('/goals/save/<card_id>', methods=['GET', 'POST'])
def goals_save_goals(card_id):
    goals_text = request.args.get(f"goals_{card_id}")
    return DataUtils().save_goals_for_specific_cards(card_id, goals_text)


@app.route('/vote', methods=['GET', 'POST'])
def vote_page():
    active_user = get_active_user()
    if not active_user:
        return redirect(url_for('login'))

    show_voting = Settings().get_specific_setting("show_voting")
    filtered_cards = []
    already_voted = False
    if show_voting:
        points = DataUtils().get_points()
        users_voted = [elem.get("author") for elem in points]
        if active_user.get("name") in users_voted:
            already_voted = True
        else:
            filtered_cards = DataUtils().get_visible_cards()
            filtered_cards.sort(key=lambda c: c.get("id"), reverse=False)

    return render_template('/vote.html', title="Vote", active_user=active_user, cards=filtered_cards,
                           already_voted=already_voted, show_voting=show_voting)


@app.route('/vote_on_cards', methods=['GET', 'POST'])
def vote_on_cards():
    active_user = get_active_user()
    if not active_user:
        return redirect(url_for('permission_denied'))

    show_voting = Settings().get_specific_setting("show_voting")
    points = DataUtils().get_points()
    users_voted = [elem.get("author") for elem in points]
    if active_user.get("name") in users_voted or not show_voting:
        message = "You have already voted."
    else:
        id_6 = int(request.args.get("points_6"))
        id_3 = int(request.args.get("points_3"))
        id_1 = int(request.args.get("points_1"))
        if len({id_6, id_3, id_1}) < len([id_6, id_3, id_1]):
            message = "Duplicated cards. The Vote was canceled. Try again."
        else:
            message = DataUtils().add_votes(id_6, id_3, id_1, active_user)

    return message


@app.route('/management/card/<card_id>', methods=['GET', 'POST'])
def edit_card(card_id):
    active_user = get_active_user()
    if not active_user or active_user.get("role") != "admin":
        return redirect(url_for('permission_denied'))

    card = DataUtils().get_card_by_id(card_id)
    return render_template('/management/management_edit_card.html', title="Edit card",
                           active_user=active_user, card=card)


@app.route('/management/cards/<card_id>/save_new_data', methods=['GET', 'POST'])
def management_card_save_new_data(card_id):
    active_user = get_active_user()
    if not active_user or active_user.get("role") != "admin":
        return redirect(url_for('permission_denied'))

    card_emotions = request.args.get("card_emotions").capitalize() if request.args.get("card_emotions") else ""
    card_text = request.args.get("card_text") if request.args.get("card_text") else ""
    card_type = request.args.get("card_type") if request.args.get("card_type") else ""
    card_points = request.args.get("card_points") if request.args.get("card_points") else ""
    new_card = {"emotions": card_emotions, "name": card_text, "type": card_type}
    if card_points:
        new_card["points"] = card_points

    message = DataUtils().edit_card_data(card_id, new_card)
    return message


@app.route('/management/users/add_user', methods=['GET', 'POST'])
def management_add_user():
    active_user = get_active_user()
    if not active_user or active_user.get("role") != "admin":
        return redirect(url_for('permission_denied'))

    name = request.args.get('user_name', '')
    initials = request.args.get('user_initials', '')
    role = request.args.get('user_role', '')
    pin = request.args.get('user_pin', '')
    encoded_pin = str(hashlib.md5(pin.encode("utf-8")).hexdigest())
    user_data = {
        'card_color': request.args.get('user_card_color', ''),
        'color': request.args.get('user_bg_color', ''),
        'icon': request.args.get('user_icon', ''),
        'id': DataUtils().get_max_user_id(),
        'initials': initials,
        'name': name,
        'passwd': encoded_pin,
        'role': role,
    }
    if name and initials and role:
        DataUtils().add_user(user_data)
        message = f"Done. User '{name}' (role: {role}) was added."
    else:
        message = "Error. Wrong input data."
    return message


@app.route('/management/users/add_user_form', methods=['GET', 'POST'])
def management_add_user_form():
    active_user = get_active_user()
    if not active_user or active_user.get("role") != "admin":
        return redirect(url_for('permission_denied'))

    return render_template('management/component/user_add_form.html')


@app.route('/management/show_vote/<vote_id>', methods=['GET', 'POST'])
def show_vote(vote_id):
    active_user = get_active_user()
    if not active_user or active_user.get("role") != "admin":
        return redirect(url_for('permission_denied'))

    DataUtils().vote_show_hide(vote_id)
    return redirect(url_for('management_cards'))


@app.route('/management/panel', methods=['GET', 'POST'])
def management_panel():
    active_user = get_active_user()
    if not active_user or active_user.get("role") != "admin":
        return redirect(url_for('permission_denied'))

    params = {
        'users': DataUtils().get_users(),
        'settings': Settings().get_settings(),
        'cards': DataUtils().get_cards(),
    }
    return render_template('/management/management_panel.html', title="Management panel",
                           active_user=active_user, params=params)


@app.route('/management/user/<user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    active_user = get_active_user()
    if not active_user or active_user.get("role") not in ["admin"]:
        return redirect(url_for('permission_denied'))

    user = DataUtils().get_user_by_id(user_id)
    return render_template('/management/management_edit_user.html', title="Edit user",
                           active_user=active_user, user=user)


@app.route('/management/user/<user_id>/save_new_data', methods=['GET', 'POST'])
def management_edit_user_save_new_data(user_id):
    active_user = get_active_user()
    if not active_user or active_user.get("role") not in ["admin"]:
        return redirect(url_for('permission_denied'))

    user_initials = request.args.get("user_initials") if request.args.get("user_initials") else ""
    user_name = request.args.get("user_name") if request.args.get("user_name") else ""
    user_icon = request.args.get("user_icon") if request.args.get("user_icon") else ""
    user_color = request.args.get("user_color") if request.args.get("user_color") else ""
    user_card_color = request.args.get("user_card_color") if request.args.get("user_card_color") else ""
    active_user = get_active_user()
    if active_user.get("role") in ["admin"]:
        user_role = request.args.get("user_role") if request.args.get("user_role") else "user"
    else:
        user_role = active_user.get("role")

    new_user_data = {"initials": user_initials, "name": user_name, "icon": user_icon, "color": user_color,
                     "card_color": user_card_color, "role": user_role}
    message = DataUtils().update_user_data(user_id, new_user_data)
    return message


@app.route('/management/users/get_table', methods=['GET', 'POST'])
def management_users_get_table():
    active_user = get_active_user()
    if not active_user:
        return redirect(url_for('login'))

    users = DataUtils().get_users()
    return render_template('management/component/users_table.html', users=users)


@app.route('/management/cards/get_table', methods=['GET', 'POST'])
def management_cards_get_table():
    active_user = get_active_user()
    if not active_user:
        return redirect(url_for('permission_denied'))

    cards = DataUtils().get_cards()
    return render_template('components/cards_table.html', cards=cards)


@app.route('/management/settings/get_table', methods=['GET', 'POST'])
def management_settings_get_table():
    active_user = get_active_user()
    if not active_user:
        return redirect(url_for('permission_denied'))

    settings_data = Settings().get_settings()
    return render_template('management/component/settings_table.html', settings=settings_data)


@app.route('/management/settings/set/<name>', methods=['GET', 'POST'])
def settings_set(name):
    active_user = get_active_user()
    if not active_user:
        return redirect(url_for('permission_denied'))

    Settings().set_new_value(name)
    settings_data = Settings().get_settings()
    return render_template('management/component/settings_table.html', settings=settings_data)


# [ERRORS]
@app.errorhandler(404)
def not_found(error):
    active_user = get_active_user()
    return render_template('message_page.html', title="Page not found.",
                           message=f"Something went wrong. 😢. <br>Error: {error}", active_user=active_user)


# [LOCAL]
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
