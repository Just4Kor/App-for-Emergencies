class SearchEngine:
    def filter_by_location(self, workers, location):
        return [
            worker for worker in workers
            if worker.location.lower() == location.lower()
        ]

    def filter_by_specialty(self, workers, specialty):
        return [
            worker for worker in workers
            if worker.specialty.lower() == specialty.lower()
        ]

    def sort_by_rating(self, workers):
        return sorted(
            workers,
            key = lambda worker: worker.rating,
            reverse = True
        )
