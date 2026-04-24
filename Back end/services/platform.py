from models.request import ServiceRequest
from services.search import SearchEngine


class Platform:
    def __init__(self):
        self.users = []
        self.workers = []
        self.requests = []
        self.search_engine = SearchEngine()

    def add_user(self, user):
        self.users.append(user)

    def add_worker(self, worker):
        self.workers.append(worker)

    def create_request(self, user, worker, title, description):
        request_id = len(self.requests) + 1

        request = ServiceRequest(
            request_id,
            user,
            worker,
            title,
            description
        )

        self.requests.append(request)
        user.add_request(request)

        return request

    def find_workers_by_location(self, location):
        return self.search_engine.filter_by_location(
            self.workers,
            location
        )

    def find_workers_by_specialty(self, specialty):
        return self.search_engine.filter_by_specialty(
            self.workers,
            specialty
        )

    def get_best_workers(self):
        return self.search_engine.sort_by_rating(self.workers)
