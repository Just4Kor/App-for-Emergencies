class Rating:
    def __init__(self):
        self.scores = []

    def add_score(self, score):
        score = float(score)

        if score < 0 or score > 5:
            raise ValueError("Rating must be between 0 and 5.")

        self.scores.append(score)

    def get_average(self):
        if not self.scores:
            return 5.0

        return sum(self.scores) / len(self.scores)
