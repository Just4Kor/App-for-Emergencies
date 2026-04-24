from abc import ABC, abstractmethod


class Person(ABC):
    def __init__(self, person_id, name, location):
        self.person_id = person_id
        self.name = name
        self.location = location

    @abstractmethod
    def get_profile_summary(self):
        pass
