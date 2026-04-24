from web_models.account import BaseAccount


class WorkerAccountModel(BaseAccount):
    def __init__(
        self,
        username,
        password,
        specialty,
        location,
        hourly_rate
    ):
        super().__init__(username, password)
        self.specialty = specialty
        self.location = location
        self.hourly_rate = hourly_rate
        self.rating = 5

    def get_role(self):
        return "worker"
