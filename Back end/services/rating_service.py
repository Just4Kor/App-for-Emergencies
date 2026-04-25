class RatingService:
    def get_worker_rating(self, worker):
        return worker.get_rating()

    def calculate_average(self, scores):
        if not scores:
            return 5.0

        return sum(scores) / len(scores)
