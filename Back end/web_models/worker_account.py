from web_models.account import AccountView


class WorkerView(AccountView):
    def __init__(self, worker):
        super().__init__(worker)
        self.specialty = worker.specialty
        self.location = worker.location
        self.hourly_rate = worker.hourly_rate
        self.rating = worker.get_rating()
