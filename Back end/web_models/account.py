from abc import ABC, abstractmethod


class BaseAccount(ABC):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    @abstractmethod
    def get_role(self):
        pass
