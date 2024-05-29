#  """
#  -----------------------------------------------------------------------
#  Designed and implemented by bartiniem
#  -----------------------------------------------------------------------
#  """

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
        with open(dict_file, 'w') as file:
            yaml.dump(my_data, file, default_flow_style=False)

    @staticmethod
    def load_yaml_data(dict_file):
        with open(dict_file, "r", encoding="utf-8") as file:
            yaml_data = yaml.load(file, Loader=yaml.Loader)
            return yaml_data

    @staticmethod
    def get_cards():
        cards = DataUtils().load_yaml_data(CARDS_FILE)
        for card in cards:
            points_sum = 0
            if card.get("points"):
                for points in card.get("points").replace(",", " ").strip().split():
                    points_sum += int(points)
            card["points_sum"] = points_sum
        return cards

    def save_users(self, users):
        self.save_data_to_yaml(users, USERS_FILENAME)

    def save_cards(self, cards):
        self.save_data_to_yaml(cards, CARDS_FILE)

    def save_votes(self, votes):
        self.save_data_to_yaml(votes, VOTES_FILE)

    def save_points(self, votes):
        self.save_data_to_yaml(votes, POINTS_FILE)

    @staticmethod
    def get_card_by_id(card_id):
        cards = DataUtils().load_yaml_data(CARDS_FILE)
        matched_card = {}
        for card in cards:
            if str(card.get("id")) == str(card_id):
                matched_card = card
        return matched_card

    def get_users(self):
        users = self.load_yaml_data(USERS_FILENAME)
        return users

    def get_user(self, name):
        users = self.load_yaml_data(USERS_FILENAME)
        user = [user for user in users if user.get("name") == name]
        return user[0] if user else {}

    def get_user_by_name(self, username):
        users = self.load_yaml_data(USERS_FILENAME)
        user = [user for user in users if user.get("name") == username]
        return user[0] if user else {}

    def get_user_by_id(self, user_id):
        users = self.load_yaml_data(USERS_FILENAME)
        user = [user for user in users if str(user.get("id")) == str(user_id)]
        return user[0] if user else {}

    def get_user_initials(self, username):
        user = self.get_user_by_name(username)
        return user.get("initials") if user else {}

    @staticmethod
    def update_points_emoji(cards):
        sorted_points = sorted([card.get("points_sum") for card in cards], reverse=True)
        for card in cards:
            if len(sorted_points) > 0 and card["points_sum"] == sorted_points[0]:
                card["points_emoji"] = '<i class="caret right icon"></i><i class="yellow medal icon"></i>1'
            if len(sorted_points) > 1 and card["points_sum"] == sorted_points[1]:
                card["points_emoji"] = '<i class="caret right icon"></i><i class="grey medal icon"></i> 2'
            if len(sorted_points) > 2 and card["points_sum"] == sorted_points[2]:
                card["points_emoji"] = '<i class="caret right icon"></i><i class="brown medal icon"></i> 3'
        return cards

    def update_user_data(self, cards):
        for card in cards:
            user = self.get_user(card.get("author"))
            card["author_initials"] = user.get("initials") if user else card["author"][0:2]
            card["author_icon"] = user.get("icon") if user else card["author"]
            card["author_color"] = user.get("color") if user else "#333"
            card["card_color"] = user.get("card_color") if user else "#ceb553"
        return cards

    def update_votes_data(self, votes):
        for vote in votes:
            user = self.get_user(vote.get("author"))
            vote["author_initials"] = user.get("initials") if user else vote["author"][0:2]
            vote["author_icon"] = user.get("icon") if user else vote["author"]
            vote["author_color"] = user.get("color") if user else "#333"
        return votes

    @staticmethod
    def get_votes():
        votes = DataUtils().load_yaml_data(VOTES_FILE)
        return votes

    @staticmethod
    def get_points():
        votes = DataUtils().load_yaml_data(POINTS_FILE)
        return votes

    @staticmethod
    def get_points_for_cards():
        sum_points = 0
        cards = DataUtils().load_yaml_data(CARDS_FILE)
        for card in cards:
            points_sum = 0
            if card.get("points"):
                for points in card.get("points").replace(",", " ").strip().split():
                    points_sum += int(points)
            card["points_sum"] = points_sum
            sum_points += points_sum
        return sum_points

    def get_visible_cards(self):
        cards = self.get_cards()
        return [card for card in cards if bool(card.get("show"))]
