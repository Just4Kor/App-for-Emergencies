from werkzeug.security import generate_password_hash


class AccountFactory:
    @staticmethod
    def create_customer(account_class, username, password, city):
        return account_class(
            role = "customer",
            username = username,
            password = generate_password_hash(password),
            city = city,
        )

    @staticmethod
    def create_worker(
        account_class,
        username,
        password,
        specialty,
        location,
        hourly_rate
    ):
        return account_class(
            role = "worker",
            username = username,
            password = generate_password_hash(password),
            specialty = specialty,
            location = location,
            hourly_rate = hourly_rate,
            rating = 5.0,
        )
