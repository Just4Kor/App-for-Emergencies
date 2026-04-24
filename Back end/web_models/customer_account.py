from web_models.account import BaseAccount


class CustomerAccountModel(BaseAccount):
    def __init__(self, username, password, city):
        super().__init__(username, password)
        self.city = city

    def get_role(self):
        return "customer"
