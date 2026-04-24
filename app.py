from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash

from factory.account_factory import AccountFactory
from services.worker_file_service import (
    load_workers_from_file,
    save_worker_to_file,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///emergency_services.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"


SPECIALTIES = [
    "Plumber",
    "Electrician",
    "Mechanic",
    "Carpenter",
    "Painter",
    "Locksmith",
    "HVAC Technician",
]

CITIES = [
    "Vilnius",
    "Kaunas",
    "Klaipeda",
    "Siauliai",
    "Panevezys",
    "Alytus",
    "Marijampole",
    "Utena",
]


class Account(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    role = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    city = db.Column(db.String(80))

    specialty = db.Column(db.String(80))
    location = db.Column(db.String(80))
    hourly_rate = db.Column(db.Float)
    rating = db.Column(db.Float, default=5.0)


class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    customer_id = db.Column(db.Integer, nullable=False)
    worker_id = db.Column(db.Integer, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Account, int(user_id))


def import_workers_from_txt():
    file_workers = load_workers_from_file()

    for worker_data in file_workers:
        existing_worker = Account.query.filter_by(
            username=worker_data["username"]
        ).first()

        if existing_worker:
            continue

        worker = Account(
            role="worker",
            username=worker_data["username"],
            password="imported_worker",
            specialty=worker_data["specialty"],
            location=worker_data["location"],
            hourly_rate=worker_data["hourly_rate"],
            rating=worker_data["rating"],
        )

        db.session.add(worker)

    db.session.commit()


@app.route("/")
def home():
    selected_location = request.args.get("location", "")
    selected_specialty = request.args.get("specialty", "")

    workers_query = Account.query.filter_by(role="worker")

    if selected_location:
        workers_query = workers_query.filter_by(location=selected_location)

    if selected_specialty:
        workers_query = workers_query.filter_by(specialty=selected_specialty)

    workers = workers_query.order_by(Account.rating.desc()).all()

    return render_template(
        "index.html",
        workers=workers,
        cities=CITIES,
        locations=CITIES,
        specialties=SPECIALTIES,
        selected_location=selected_location,
        selected_specialty=selected_specialty,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        role = request.form["role"]
        username = request.form["username"]
        password = request.form["password"]

        existing_account = Account.query.filter_by(username=username).first()

        if existing_account:
            flash("Username already exists.", "error")
            return redirect(url_for("register"))

        if role == "customer":
            account = AccountFactory.create_customer(
                Account,
                username,
                password,
                request.form["city"],
            )

        elif role == "worker":
            account = AccountFactory.create_worker(
                Account,
                username,
                password,
                request.form["specialty"],
                request.form["location"],
                float(request.form["hourly_rate"]),
            )

        else:
            flash("Invalid account type.", "error")
            return redirect(url_for("register"))

        db.session.add(account)
        db.session.commit()

        if role == "worker":
            save_worker_to_file(account)

        flash("Account created successfully.", "success")
        return redirect(url_for("login"))

    return render_template(
        "register.html",
        cities=CITIES,
        locations=CITIES,
        specialties=SPECIALTIES,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        account = Account.query.filter_by(
            username=request.form["username"]
        ).first()

        if account and check_password_hash(
            account.password,
            request.form["password"],
        ):
            login_user(account)

            if account.role == "worker":
                return redirect(url_for("worker_dashboard"))

            return redirect(url_for("home"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "success")
    return redirect(url_for("home"))


@app.route("/worker/<int:worker_id>", methods=["GET", "POST"])
@login_required
def worker_details(worker_id):
    worker = db.session.get(Account, worker_id)

    if worker is None or worker.role != "worker":
        flash("Worker not found.", "error")
        return redirect(url_for("home"))

    if current_user.role != "customer":
        flash("Only customers can send requests.", "error")
        return redirect(url_for("home"))

    if request.method == "POST":
        request_count = ServiceRequest.query.filter_by(
            customer_id=current_user.id
        ).count()

        if request_count >= 5:
            oldest_request = ServiceRequest.query.filter_by(
                customer_id=current_user.id
            ).order_by(ServiceRequest.created_at.asc()).first()

            if oldest_request:
                db.session.delete(oldest_request)

        service_request = ServiceRequest(
            title=request.form["title"],
            description=request.form["description"],
            customer_id=current_user.id,
            worker_id=worker.id,
        )

        db.session.add(service_request)
        db.session.commit()

        flash("Request sent successfully.", "success")
        return redirect(url_for("my_requests"))

    return render_template("worker_details.html", worker=worker)


@app.route("/my_requests")
@login_required
def my_requests():
    if current_user.role != "customer":
        return redirect(url_for("home"))

    requests_data = ServiceRequest.query.filter_by(
        customer_id=current_user.id
    ).order_by(ServiceRequest.created_at.desc()).all()

    return render_template("requests.html", requests_data=requests_data)


@app.route("/worker_dashboard")
@login_required
def worker_dashboard():
    if current_user.role != "worker":
        return redirect(url_for("home"))

    requests_data = ServiceRequest.query.filter_by(
        worker_id=current_user.id
    ).order_by(ServiceRequest.created_at.desc()).all()

    return render_template("worker_dashboard.html", requests_data=requests_data)


@app.route("/update_request/<int:request_id>", methods=["POST"])
@login_required
def update_request(request_id):
    if current_user.role != "worker":
        return redirect(url_for("home"))

    service_request = db.session.get(ServiceRequest, request_id)

    if service_request is None:
        flash("Request not found.", "error")
        return redirect(url_for("worker_dashboard"))

    if service_request.worker_id != current_user.id:
        flash("You cannot update this request.", "error")
        return redirect(url_for("worker_dashboard"))

    action = request.form["action"]

    if action == "accept":
        service_request.status = "Accepted"

    if action == "deny":
        service_request.status = "Denied"

    db.session.commit()

    flash("Request updated.", "success")
    return redirect(url_for("worker_dashboard"))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_user.username = request.form["username"]

        if current_user.role == "customer":
            current_user.city = request.form["city"]

        if current_user.role == "worker":
            current_user.location = request.form["location"]
            current_user.hourly_rate = float(request.form["hourly_rate"])

        db.session.commit()

        flash("Profile updated.", "success")
        return redirect(url_for("profile"))

    request_count = 0

    if current_user.role == "customer":
        request_count = ServiceRequest.query.filter_by(
            customer_id=current_user.id
        ).count()

    return render_template(
        "profile.html",
        cities=CITIES,
        locations=CITIES,
        specialties=SPECIALTIES,
        request_count=request_count,
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        import_workers_from_txt()

    app.run(debug=True)
