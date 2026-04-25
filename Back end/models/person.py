from abc import ABC, abstractmethod


class Person(ABC):
    def __init__(self, person_id, username, location=""):
        self.id = str(person_id)
        self.username = username
        self.location = location

    @abstractmethod
    def get_profile_summary(self):
        pass
