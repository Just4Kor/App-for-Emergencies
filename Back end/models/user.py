from flask_login import UserMixin

from models.person import Person


class User(Person, UserMixin):
    def __init__(self, user_id, username, password, city):
        super().__init__(user_id, username, city)
        self.password = password
        self.city = city
        self.role = "customer"

    def get_profile_summary(self):
        return f"Customer: {self.username}, City: {self.city}"
