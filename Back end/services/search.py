from services.rating_service import RatingService


class SearchEngine:
    def __init__(self):
        self.rating_service = RatingService()

    def filter_workers(self, workers, location="", specialty=""):
        result = workers

        if location:
            result = [
                worker for worker in result
                if worker.location == location
            ]

        if specialty:
            result = [
                worker for worker in result
                if worker.specialty == specialty
            ]

        return result

    def sort_workers(self, workers):
        return sorted(
            workers,
            key=lambda worker: self.rating_service.get_worker_rating(worker),
            reverse=True,
        )
