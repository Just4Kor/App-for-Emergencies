from models.person import Person


class User(Person):
    def __init__(self, person_id, name, location, city):
        super().__init__(person_id, name, location)
        self.city = city
        self.requests = []

    def add_request(self, request):
        if len(self.requests) >= 5:
            self.requests.pop(0)
        self.requests.append(request)

    def update_city(self, city):
        self.city = city

    def get_profile_summary(self):
        return f"User: {self.name}, City: {self.city}"
