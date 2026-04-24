class RatingService:
    def __init__(self):
        self.ratings = []

    def add_rating(self, rating):
        self.ratings.append(rating)
        self.update_worker_average(rating.worker)

    def get_worker_ratings(self, worker):
        return [
            rating for rating in self.ratings
            if rating.worker == worker
        ]

    def get_average_rating(self, worker):
        worker_ratings = self.get_worker_ratings(worker)

        if not worker_ratings:
            return worker.rating

        total = sum(rating.score for rating in worker_ratings)
        return round(total / len(worker_ratings), 2)

    def update_worker_average(self, worker):
        average = self.get_average_rating(worker)
        worker.update_rating(average)
