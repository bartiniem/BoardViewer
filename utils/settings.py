#  """
#  -----------------------------------------------------------------------
#  Designed and implemented by bartiniem
#  -----------------------------------------------------------------------
#  """
"""Settings module"""

from utils.data_files_utils import DataFilesUtils

SETTINGS_FILENAME = "./data/settings.yaml"


class Settings:
    """Settings class"""

    def __init__(self):
        pass

    @staticmethod
    def save_data_to_yaml(my_data, dict_file):
        """Save data to base"""
        DataFilesUtils().save_data_to_yaml(my_data, dict_file)

    @staticmethod
    def load_yaml_data(dict_file):
        """Read database"""
        return DataFilesUtils().load_yaml_data(dict_file)

    def get_settings(self):
        """Get Settings"""
        settings = self.load_yaml_data(SETTINGS_FILENAME)
        return settings

    def get_specific_setting(self, name: str):
        """Get Setting by name"""
        settings = self.get_settings()
        return settings.get(name, '')

    def set_new_value(self, name: str):
        """Set new value for bool"""
        settings = self.get_settings()
        settings[name] = not settings[name]
        self.save_settings(settings)

    def save_settings(self, settings_data):
        """Save specific settings"""
        self.save_data_to_yaml(settings_data, SETTINGS_FILENAME)
