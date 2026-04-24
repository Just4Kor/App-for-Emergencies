from models.person import Person


class Worker(Person):
    def __init__(self, person_id, name, location, specialty, rate, rating=5):
        super().__init__(person_id, name, location)
        self.specialty = specialty
        self.rate = rate
        self.rating = rating

    @property
    def rate(self):
        return self._rate

    @rate.setter
    def rate(self, value):
        if value <= 0:
            raise ValueError("Rate must be greater than 0.")
        self._rate = value

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value):
        if value < 0 or value > 5:
            raise ValueError("Rating must be between 0 and 5.")
        self._rating = value

    def update_rating(self, rating):
        self.rating = rating

    def get_profile_summary(self):
        return (
            f"{self.name} is a {self.specialty} in {self.location}. "
            f"Rate: {self.rate}€/h, Rating: {self.rating}/5"
        )
