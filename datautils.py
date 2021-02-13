#  """
#  -----------------------------------------------------------------------
#  Designed and implemented by bartiniem
#  -----------------------------------------------------------------------
#  """

import yaml

USERS_FILENAME = "data/users.yaml"

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
            yaml_data = yaml.load(file, Loader=yaml.FullLoader)
            return yaml_data

    @staticmethod
    def get_cards(filename):
        cards = DataUtils().load_yaml_data(filename)
        for card in cards:
            points_sum = 0
            if card.get("points"):
                for points in card.get("points").split(","):
                    points_sum += int(points)
            card["points_sum"] = points_sum
        return cards

    @staticmethod
    def get_card_by_id(filename, card_id):
        cards = DataUtils().load_yaml_data(filename)
        matched_card = {}
        for card in cards:
            if str(card.get("id")) == str(card_id):
                matched_card = card
        return matched_card

    def get_users(self):
        users = self.load_yaml_data(USERS_FILENAME)
        return users

    def get_user(self, initials):
        users = self.load_yaml_data(USERS_FILENAME)
        user = [user for user in users if user.get("initials") == initials]
        return user[0] if user else {}

    def update_user_data(self, cards):
        for card in cards:
            user = self.get_user(card.get("author"))
            card["author_icon"] = user.get("icon") if user else card["author"]
            card["author_color"] = user.get("color") if user else "#333"""
        return cards

    def update_votes_data(self, votes):
        for vote in votes:
            user = self.get_user(vote.get("author"))
            vote["author_icon"] = user.get("icon") if user else vote["author"]
            vote["author_color"] = user.get("color") if user else "#333"
        return votes



