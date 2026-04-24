class WorkerRating:
    def __init__(self, user, worker, score, comment=""):
        self.user = user
        self.worker = worker
        self.score = score
        self.comment = comment

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        if value < 1 or value > 5:
            raise ValueError("Rating must be between 1 and 5.")
        self._score = value

    def update_rating(self, score, comment=""):
        self.score = score
        self.comment = comment
