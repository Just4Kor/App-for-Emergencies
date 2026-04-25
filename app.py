from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from factory.account_factory import AccountFactory
from models.request import ServiceRequest
from services.platform import Platform
from services.worker_file_service import (
    create_files_if_missing,
    find_account_by_id,
    find_account_by_username,
    get_next_customer_id,
    get_next_request_id,
    get_next_worker_id,
    read_customers,
    read_requests,
    read_workers,
    save_customers,
    save_requests,
    save_workers,
    update_account,
)
from web_models.customer_account import CustomerView
from web_models.worker_account import WorkerView

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"

login_manager = LoginManager(app)
login_manager.login_view = "login"

platform = Platform()

CITIES = [
    "Vilnius",
    "Kaunas",
    "Klaipėda",
    "Šiauliai",
    "Panevėžys",
    "Alytus",
]

SPECIALTIES = [
    "Plumber",
    "Electrician",
    "Mechanic",
    "Carpenter",
    "Painter",
]


@login_manager.user_loader
def load_user(user_id):
    return find_account_by_id(user_id)


@app.route("/")
def home():
    selected_location = request.args.get("location", "")
    selected_specialty = request.args.get("specialty", "")

    workers = platform.get_workers(
        location=selected_location,
        specialty=selected_specialty,
    )

    worker_views = [
        WorkerView(worker) for worker in workers
    ]

    return render_template(
        "index.html",
        workers = worker_views,
        locations = CITIES,
        cities = CITIES,
        specialties = SPECIALTIES,
        selected_location = selected_location,
        selected_specialty = selected_specialty,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        role = request.form["role"]
        username = request.form["username"]
        password = request.form["password"]

        if find_account_by_username(username):
            flash("Username already exists.", "error")
            return redirect(url_for("register"))

        if role == "customer":
            customers = read_customers()

            customer = AccountFactory.create_customer(
                user_id = get_next_customer_id(),
                username = username,
                password = password,
                city = request.form["city"],
            )

            customers.append(customer)
            save_customers(customers)

        elif role == "worker":
            workers = read_workers()

            worker = AccountFactory.create_worker(
                worker_id = get_next_worker_id(),
                username = username,
                password = password,
                specialty = request.form["specialty"],
                location = request.form["location"],
                hourly_rate = request.form["hourly_rate"],
            )

            workers.append(worker)
            save_workers(workers)

        else:
            flash("Invalid account type.", "error")
            return redirect(url_for("register"))

        flash("Account created successfully.", "success")
        return redirect(url_for("login"))

    return render_template(
        "register.html",
        cities = CITIES,
        locations = CITIES,
        specialties = SPECIALTIES,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        account = find_account_by_username(username)

        if account and account.password == password:
            login_user(account)

            if account.role == "worker":
                return redirect(url_for("worker_dashboard"))

            return redirect(url_for("home"))

        flash("Wrong username or password.", "error")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "success")
    return redirect(url_for("home"))


@app.route("/worker/<worker_id>", methods=["GET", "POST"])
@login_required
def worker_details(worker_id):
    worker = find_account_by_id(worker_id)

    if worker is None or worker.role != "worker":
        flash("Worker not found.", "error")
        return redirect(url_for("home"))

    if current_user.role != "customer":
        flash("Only customers can send requests.", "error")
        return redirect(url_for("home"))

    if request.method == "POST":
        requests_list = read_requests()

        customer_requests = platform.get_customer_requests(current_user.id)

        if len(customer_requests) >= 5:
            oldest_request = customer_requests[0]
            requests_list.remove(oldest_request)

        new_request = ServiceRequest(
            request_id = get_next_request_id(),
            title = request.form["title"],
            description = request.form["description"],
            address = request.form["address"],
            status = "Pending",
            customer_id = current_user.id,
            worker_id = worker.id,
        )

        requests_list.append(new_request)
        save_requests(requests_list)

        flash("Request sent successfully.", "success")
        return redirect(url_for("my_requests"))

    worker_view = WorkerView(worker)

    return render_template("worker_details.html", worker = worker_view)


@app.route("/my_requests")
@login_required
def my_requests():
    if current_user.role != "customer":
        return redirect(url_for("home"))

    requests_data = platform.get_customer_requests(current_user.id)

    return render_template("requests.html", requests_data = requests_data)


@app.route("/worker_dashboard")
@login_required
def worker_dashboard():
    if current_user.role != "worker":
        return redirect(url_for("home"))

    requests_data = platform.get_worker_requests(current_user.id)
    worker_view = WorkerView(current_user)

    return render_template(
        "worker_dashboard.html",
        requests_data = requests_data,
        worker = worker_view,
    )


@app.route("/update_request/<request_id>", methods=["POST"])
@login_required
def update_request(request_id):
    if current_user.role != "worker":
        return redirect(url_for("home"))

    requests_list = read_requests()
    action = request.form["action"]

    for item in requests_list:
        if item.id == request_id and item.worker_id == current_user.id:
            if action == "accept":
                item.accept()

            if action == "deny":
                item.deny()

            save_requests(requests_list)
            flash("Request updated.", "success")
            return redirect(url_for("worker_dashboard"))

    flash("Request not found.", "error")
    return redirect(url_for("worker_dashboard"))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_user.username = request.form["username"]

        if current_user.role == "customer":
            current_user.city = request.form["city"]
            current_user.location = request.form["city"]

        if current_user.role == "worker":
            current_user.location = request.form["location"]
            current_user.hourly_rate = request.form["hourly_rate"]

        update_account(current_user)

        flash("Profile updated.", "success")
        return redirect(url_for("profile"))

    request_count = 0
    user_view = None

    if current_user.role == "customer":
        request_count = len(
            platform.get_customer_requests(current_user.id)
        )
        user_view = CustomerView(current_user)

    if current_user.role == "worker":
        user_view = WorkerView(current_user)

    return render_template(
        "profile.html",
        cities = CITIES,
        locations = CITIES,
        specialties = SPECIALTIES,
        request_count = request_count,
        user_view = user_view,
    )


if __name__ == "__main__":
    create_files_if_missing()
    app.run(debug=True)
