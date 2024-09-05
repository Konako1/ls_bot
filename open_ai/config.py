import configparser
import pathlib


class Config:
    config = configparser.ConfigParser()
    config_path = pathlib.Path(__file__).parent.absolute() / "config.ini"

    @staticmethod
    def read(variable: str):
        Config.config.read(Config.config_path, encoding='utf-8')

        path = variable.split('.')
        if len(path) == 1:
            return Config.config[variable]
        return Config.config[path[0]][path[1]]


    @staticmethod
    def write(variable: str, value):
        Config.config.read(Config.config_path, encoding='utf-8')

        path = variable.split('.')
        Config.config[path[0]][path[1]] = str(value)

        with open(Config.config_path, 'w', encoding='utf-8') as configfile:
            Config.config.write(configfile)
