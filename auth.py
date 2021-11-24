import config


class Authorizer:
    def __init__(self):
        self.admin_password = config.authorization()

    def authorize(self, password):
        if self.admin_password == password:
            return True
        return False
