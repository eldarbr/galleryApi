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

    def yadisk_api(self):
        folder = self.config["YADISK.API"]["remote_folder"]
        if folder[-1] != "/":
            folder += "/"
        return self.config["YADISK.API"]["api_token"], folder

    def yadisk_api_rewrite(self, token, remote_folder):
        """
        Re-configurator for api module
        :param token: token to be saved
        :param remote_folder: remote folder to be saved
        """
        original_token, original_folder = self.yadisk_api()
        if token is None:
            token = original_token
        if remote_folder is None:
            remote_folder = original_folder
        self.config.set("YADISK.API", "api_token", token)
        self.config.set("YADISK.API", "remote_folder", remote_folder)
        with open("config.ini", "w") as configfile:
            self.config.write(configfile)
