#  """
#  -----------------------------------------------------------------------
#  Designed and implemented by bartiniem
#  -----------------------------------------------------------------------
#  """
from datetime import datetime
import yaml

USERS_FILENAME = "./data/users.yaml"
CARDS_FILE = "./data/cards.yaml"
VOTES_FILE = "./data/votes.yaml"
POINTS_FILE = "./data/points.yaml"


class DataUtils:

    def __init__(self):
        pass

    @staticmethod
    def save_data_to_yaml(my_data, dict_file):
        with open(dict_file, 'w', encoding="utf-8") as file:
            yaml.dump(my_data, file, default_flow_style=False)

    @staticmethod
    def load_yaml_data(dict_file):
        with open(dict_file, "r", encoding="utf-8") as file:
            yaml_data = yaml.load(file, Loader=yaml.Loader)
            return yaml_data

    def get_cards(self) -> list:
        cards = self.load_yaml_data(CARDS_FILE)
        for card in cards:
            points_sum = 0
            if card.get("points"):
                for points in card.get("points").replace(",", " ").strip().split():
                    points_sum += int(points)
            card["points_sum"] = points_sum
        return cards

    def add_card(self, card_data) -> str:
        cards = self.get_cards()
        id_to_set = self.get_cards_next_id()
        card_data.update({'id': id_to_set, "points": "", "show": False, "last_edit": 0})
        cards.append(card_data)
        self.save_cards(cards)
        return f"New card was added: {card_data}"

    def add_vote(self, vote_data) -> str:
        votes = self.get_votes()
        id_to_set = self.get_votes_next_id()
        vote_data.update({'id': id_to_set, "points": "", "show": False, "last_edit": 0})
        votes.append(vote_data)
        self.save_votes(votes)
        return f"New vote was added: {vote_data}"

    def get_cards_next_id(self) -> int:
        ids = [int(c.get('id')) for c in self.get_cards()]
        return max(ids) + 1

    def get_votes_next_id(self) -> int:
        ids = [int(c.get('id')) for c in self.get_votes()]
        return max(ids) + 1

    def get_card_by_id(self, card_id) -> dict:
        cards = self.get_cards()
        matched_card = {}
        for card in cards:
            if str(card.get("id")) == str(card_id):
                matched_card = card
                break
        return matched_card

    def save_users(self, users):
        self.save_data_to_yaml(users, USERS_FILENAME)

    def get_users(self) -> list:
        users = self.load_yaml_data(USERS_FILENAME)
        return users

    def get_user_by_name(self, username) -> dict:
        users = self.get_users()
        user = [user for user in users if user.get("name") == username]
        return user[0] if user else {}

    def get_user_by_id(self, user_id) -> dict:
        users = self.get_users()
        user = [user for user in users if str(user.get("id")) == str(user_id)]
        return user[0] if user else {}

    def add_user(self, user_data: dict):
        users = self.get_users()
        users.append(user_data)
        self.save_users(users)

    def get_max_user_id(self) -> int:
        users_id_max = max((int(u.get("id")) for u in self.get_users())) + 1
        return users_id_max

    def save_cards(self, cards):
        self.save_data_to_yaml(cards, CARDS_FILE)

    def save_votes(self, votes):
        self.save_data_to_yaml(votes, VOTES_FILE)

    def save_points(self, votes):
        self.save_data_to_yaml(votes, POINTS_FILE)

    def get_user_initials(self, username) -> str:
        user = self.get_user_by_name(username)
        return user.get("initials") if user else "n/a"

    @staticmethod
    def _update_points_emoji(cards) -> list:
        sorted_points = sorted([card.get("points_sum") for card in cards], reverse=True)
        for card in cards:
            if len(sorted_points) > 0 and card["points_sum"] == sorted_points[0]:
                card["points_emoji"] = '<i class="caret right icon"></i><i class="yellow medal icon"></i>1'
            if len(sorted_points) > 1 and card["points_sum"] == sorted_points[1]:
                card["points_emoji"] = '<i class="caret right icon"></i><i class="grey medal icon"></i> 2'
            if len(sorted_points) > 2 and card["points_sum"] == sorted_points[2]:
                card["points_emoji"] = '<i class="caret right icon"></i><i class="brown medal icon"></i> 3'
        return cards

    def get_cards_by_type(self, card_type="", only_visible=False) -> list:
        cards = self.get_cards()
        specified_cards = [card for card in cards if card.get("type") in [card_type]]
        if only_visible:
            specified_cards = [c for c in specified_cards if c.get('show', False)]

        specified_cards = self._update_points_emoji(specified_cards)
        specified_cards = self._update_user_data(specified_cards)
        specified_cards.sort(key=lambda c: c.get("last_edit", 0), reverse=False)
        return specified_cards

    def _update_user_data(self, cards) -> list:
        for card in cards:
            user = self.get_user_by_name(card.get("author"))
            card["author_initials"] = user.get("initials") if user else card["author"][0:2]
            card["author_icon"] = user.get("icon") if user else card["author"]
            card["author_color"] = user.get("color") if user else "#333"
            card["card_color"] = user.get("card_color") if user else "#ceb553"
        return cards

    def get_votes_with_users(self, sort_by_last_edit=False, only_visible=False) -> list:
        votes = self.get_votes()
        if only_visible:
            votes = [v for v in votes if v.get('show', False)]

        for vote in votes:
            user = self.get_user_by_name(vote.get("author"))
            vote["author_initials"] = user.get("initials") if user else vote["author"][0:2]
            vote["author_icon"] = user.get("icon") if user else vote["author"]
            vote["author_color"] = user.get("color") if user else "#333"

        if sort_by_last_edit:
            votes.sort(key=lambda c: c.get("last_edit", 0), reverse=False)
        return votes

    def get_votes(self) -> list:
        return self.load_yaml_data(VOTES_FILE)

    def get_points(self) -> list:
        return self.load_yaml_data(POINTS_FILE)

    def _get_sum_points_for_cards(self) -> int:
        sum_points = 0
        cards = self.get_cards()
        for card in cards:
            points_sum = 0
            if card.get("points"):
                for points in card.get("points").replace(",", " ").strip().split():
                    points_sum += int(points)
            card["points_sum"] = points_sum
            sum_points += points_sum
        return sum_points

    def get_stats(self) -> dict:
        cards = self.get_cards()
        sum_cards = len(cards)
        sum_points = self._get_sum_points_for_cards()
        stats = {
            'sum_cards': sum_cards,
            'sum_points': sum_points,
        }
        return stats

    def get_visible_cards(self) -> list:
        cards = self.get_cards()
        return [card for card in cards if bool(card.get("show"))]

    def add_votes(self, id_6, id_3, id_1, active_user) -> str:
        cards = self.get_cards()
        points = self.get_points()
        for card in cards:
            if card.get("id") == id_6:
                card["points"] += ",6" if card["points"] else "6"
            if card.get("id") == id_3:
                card["points"] += ",3" if card["points"] else "3"
            if card.get("id") == id_1:
                card["points"] += ",1" if card["points"] else "1"
        new_points = {"author": active_user.get("name"), "points_6": id_6, "points_3": id_3, "points_1": id_1}
        points.append(new_points)
        self.save_points(points)
        self.save_cards(cards)
        message = f"Thank you for votes. 6 points -> #{id_6} | 3 points -> #{id_3} | 1 point -> #{id_1}"
        return message

    def show_hide_card(self, card_id) -> bool:
        cards = self.get_cards()
        new_status = False
        for card in cards:
            if str(card.get("id")) == str(card_id):
                new_status = not card.get("show")
                card["show"] = not card.get("show")
                card["last_edit"] = datetime.now().timestamp()
        self.save_cards(cards)
        return new_status

    def edit_card_data(self, card_id, new_card_data: dict) -> str:
        cards = self.get_cards()
        for card in cards:
            if str(card.get("id")) == str(card_id):
                card.update(new_card_data)

        self.save_cards(cards)
        return f"Saved card data: {new_card_data}"

    def vote_show_hide(self, vote_id):
        votes = self.get_votes()
        for vote in votes:
            if str(vote.get("id")) == str(vote_id):
                vote["show"] = not vote.get("show")
                vote["last_edit"] = datetime.now().timestamp()

        self.save_votes(votes)

    def save_goals_for_specific_cards(self, card_id, goals_text) -> str:
        cards = self.get_cards()
        last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = "n/a"
        for card in cards:
            if str(card['id']) == str(card_id):
                card["goals"] = goals_text
                message = f"Saved {last_update}."

        self.save_cards(cards)
        return message

    def update_user_data(self, user_id, new_user_data) -> str:
        users = self.get_users()
        for user in users:
            if str(user.get("id")) == str(user_id):
                user.update(new_user_data)

        self.save_users(users)
        return f"Saved user data: {new_user_data}"
