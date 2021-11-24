from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")


def database():
    info = ""
    for key in config["DATABASE"]:
        info += key + "=" + config["DATABASE"][key]+" "
    return info.strip()


def authorization():
    return config["AUTHORIZATION"]["adminPassword"]
