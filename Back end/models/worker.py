from flask_login import UserMixin

from models.person import Person
from models.rating import Rating


class Worker(Person, UserMixin):
    def __init__(
        self,
        worker_id,
        username,
        password,
        specialty,
        location,
        hourly_rate,
        rating = "5",
    ):
        super().__init__(worker_id, username, location)
        self.password = password
        self.specialty = specialty
        self.hourly_rate = hourly_rate
        self.rating_object = Rating()
        self.rating_object.add_score(rating)
        self.rating = str(round(self.rating_object.get_average(), 2))
        self.role = "worker"

    def get_rating(self):
        return float(self.rating)

    def get_profile_summary(self):
        return (
            f"{self.username} - {self.specialty}, "
            f"{self.location}, {self.hourly_rate}€/h, "
            f"rating {self.rating}/5"
        )
