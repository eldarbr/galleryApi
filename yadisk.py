import requests
from config import Configurator


class API:
    def __init__(self):
        c = Configurator()
        self.token, self.remote_folder = c.yadisk_api()
        if self.token == "":
            raise Exception("No token specified in the config")

    def get_file_info(self, filepath):
        info = requests.get("https://cloud-api.yandex.net/v1/disk/resources", params={"path": filepath},
                            headers={"Authorization": "OAuth " + self.token})
        return info.json(), info.status_code

    def get_hrefs_by_id(self, photo_id):
        hrefs = {}
        suffixes = ["preview", "medium", "large"]
        for suffix in suffixes:
            filepath = self.remote_folder + suffix + photo_id + f"_{suffix}.jpg"
            info, status_code = self.get_file_info(filepath)
            if status_code == 200:
                hrefs[suffix] = info["file"]
            else:
                hrefs[suffix] = ""
        return hrefs
