from config import Configurator


class Authorizer:
    def __init__(self):
        config = Configurator()
        self.admin_password = config.authorization()

    def authorize(self, password):
        if self.admin_password == password:
            return True
        return False
