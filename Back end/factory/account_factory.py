from models.user import User
from models.worker import Worker


class AccountFactory:
    @staticmethod
    def create_customer(user_id, username, password, city):
        return User(
            user_id=user_id,
            username=username,
            password=password,
            city=city,
        )

    @staticmethod
    def create_worker(
        worker_id,
        username,
        password,
        specialty,
        location,
        hourly_rate,
    ):
        return Worker(
            worker_id = worker_id,
            username = username,
            password = password,
            specialty = specialty,
            location = location,
            hourly_rate = hourly_rate,
            rating = "5",
        )
