import configparser


class Config:
    config = configparser.ConfigParser()

    @staticmethod
    def read(variable: str):
        Config.config.read('open_ai/config.ini', encoding='utf-8')

        path = variable.split('.')
        if len(path) == 1:
            return Config.config[variable]
        return Config.config[path[0]][path[1]]


    @staticmethod
    def write(variable: str, value):
        Config.config.read('open_ai/config.ini', encoding='utf-8')

        path = variable.split('.')
        Config.config[path[0]][path[1]] = str(value)

        with open('open_ai/config.ini', 'w', encoding='utf-8') as configfile:
            Config.config.write(configfile)
