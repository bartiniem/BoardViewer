#  """
#  -----------------------------------------------------------------------
#  Designed and implemented by bartiniem
#  -----------------------------------------------------------------------
#  """

import yaml

SETTINGS_FILENAME = "data/settings.yaml"


class Settings:

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

    def get_settings(self):
        settings = self.load_yaml_data(SETTINGS_FILENAME)
        return settings

    def get_specific_setting(self, name: str):
        settings = self.get_settings()
        return settings.get(name, '')

    def set_new_value(self, name: str):
        settings = self.get_settings()
        settings[name] = not settings[name]
        self.save_settings(settings)

    def save_settings(self, settings_data):
        self.save_data_to_yaml(settings_data, SETTINGS_FILENAME)
