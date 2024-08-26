import configparser


class Config:
    config = configparser.ConfigParser()

    @staticmethod
    def read(variable: str):
        Config.config.read('config.ini')
        return Config.config[variable]

    @staticmethod
    def write(variable: str, value):
        Config.config.read('config.ini')
        Config.config[variable] = value
        with open('config.ini', 'w') as configfile:
            Config.config.write(configfile)
