from configparser import ConfigParser


class Configurator:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read("config.ini")

    def database(self):
        info = ""
        for key in self.config["DATABASE"]:
            info += key + "=" + self.config["DATABASE"][key]+" "
        return info.strip()

    def authorization(self):
        return self.config["AUTHORIZATION"]["adminPassword"]
