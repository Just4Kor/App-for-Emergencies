import csv
import os

from models.request import ServiceRequest
from models.user import User
from models.worker import Worker


DATA_FOLDER = "data"
WORKERS_FILE = "data/workers.txt"
CUSTOMERS_FILE = "data/customers.txt"
REQUESTS_FILE = "data/requests.txt"


def create_files_if_missing():
    os.makedirs(DATA_FOLDER, exist_ok=True)

    for file_name in [WORKERS_FILE, CUSTOMERS_FILE, REQUESTS_FILE]:
        if not os.path.exists(file_name):
            open(file_name, "w", encoding="utf-8").close()


def read_workers():
    create_files_if_missing()
    workers = []

    with open(WORKERS_FILE, "r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)

        for row in reader:
            if len(row) != 7:
                continue

            worker = Worker(
                worker_id = row[0],
                username = row[1],
                password = row[2],
                specialty = row[3],
                location = row[4],
                hourly_rate = row[5],
                rating = row[6],
            )
            workers.append(worker)

    return workers


def save_workers(workers):
    create_files_if_missing()

    with open(WORKERS_FILE, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)

        for worker in workers:
            writer.writerow([
                worker.id,
                worker.username,
                worker.password,
                worker.specialty,
                worker.location,
                worker.hourly_rate,
                worker.rating,
            ])


def read_customers():
    create_files_if_missing()
    customers = []

    with open(CUSTOMERS_FILE, "r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)

        for row in reader:
            if len(row) != 4:
                continue

            customer = User(
                user_id = row[0],
                username = row[1],
                password = row[2],
                city = row[3],
            )
            customers.append(customer)

    return customers


def save_customers(customers):
    create_files_if_missing()

    with open(CUSTOMERS_FILE, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)

        for customer in customers:
            writer.writerow([
                customer.id,
                customer.username,
                customer.password,
                customer.city,
            ])


def read_requests():
    create_files_if_missing()
    requests_list = []

    with open(REQUESTS_FILE, "r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)

        for row in reader:
            if len(row) != 7:
                continue

            service_request = ServiceRequest(
                request_id = row[0],
                title = row[1],
                description = row[2],
                address = row[3],
                status = row[4],
                customer_id = row[5],
                worker_id = row[6],
            )
            requests_list.append(service_request)

    return requests_list


def save_requests(requests_list):
    create_files_if_missing()

    with open(REQUESTS_FILE, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)

        for item in requests_list:
            writer.writerow([
                item.id,
                item.title,
                item.description,
                item.address,
                item.status,
                item.customer_id,
                item.worker_id,
            ])


def get_all_accounts():
    return read_customers() + read_workers()


def find_account_by_id(account_id):
    for account in get_all_accounts():
        if account.id == str(account_id):
            return account

    return None


def find_account_by_username(username):
    for account in get_all_accounts():
        if account.username == username:
            return account

    return None


def get_next_customer_id():
    customers = read_customers()

    if not customers:
        return "100"

    return str(max(int(customer.id) for customer in customers) + 1)


def get_next_worker_id():
    workers = read_workers()

    if not workers:
        return "1"

    return str(max(int(worker.id) for worker in workers) + 1)


def get_next_request_id():
    requests_list = read_requests()

    if not requests_list:
        return "1"

    return str(max(int(item.id) for item in requests_list) + 1)


def update_account(updated_account):
    if updated_account.role == "customer":
        customers = read_customers()

        for index, customer in enumerate(customers):
            if customer.id == updated_account.id:
                customers[index] = updated_account
                break

        save_customers(customers)

    if updated_account.role == "worker":
        workers = read_workers()

        for index, worker in enumerate(workers):
            if worker.id == updated_account.id:
                workers[index] = updated_account
                break

        save_workers(workers)
