from services.search import SearchEngine
from services.worker_file_service import (
    read_customers,
    read_requests,
    read_workers,
)


class Platform:
    def __init__(self):
        self.search_engine = SearchEngine()

    def get_workers(self, location="", specialty=""):
        workers = read_workers()
        filtered_workers = self.search_engine.filter_workers(
            workers,
            location,
            specialty,
        )
        return self.search_engine.sort_workers(filtered_workers)

    def get_customers(self):
        return read_customers()

    def get_requests(self):
        return read_requests()

    def get_customer_requests(self, customer_id):
        return [
            request for request in self.get_requests()
            if request.customer_id == str(customer_id)
        ]

    def get_worker_requests(self, worker_id):
        return [
            request for request in self.get_requests()
            if request.worker_id == str(worker_id)
        ]
