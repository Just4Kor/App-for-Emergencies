from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

from services.platform import Platform
from factory.worker_factory import WorkerFactory

app = Flask(__name__)
app.config["SECRET_KEY"] = "coursework-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///emergency_services.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

platform = Platform()


class CustomerAccount(UserMixin, db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    requests = db.relationship(
        "ServiceRequestRecord",
        backref="customer",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def role(self) -> str:
        return "customer"


class WorkerAccount(UserMixin, db.Model):
    __tablename__ = "worker_accounts"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    specialty = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Float, nullable=False, default=5.0)

    received_requests = db.relationship(
        "ServiceRequestRecord",
        backref="worker_account",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def role(self) -> str:
        return "worker"


class ServiceRequestRecord(db.Model):
    __tablename__ = "service_requests"

    id = db.Column(db.Integer, primary_key=True)
    problem_title = db.Column(db.String(120), nullable=False)
    problem_description = db.Column(db.Text, nullable=False)

    worker_name = db.Column(db.String(120), nullable=False)
    worker_specialty = db.Column(db.String(80), nullable=False)
    worker_location = db.Column(db.String(120), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Float, nullable=False)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False
    )

    worker_account_id = db.Column(
        db.Integer,
        db.ForeignKey("worker_accounts.id"),
        nullable=True
    )


@login_manager.user_loader
def load_user(user_id):
    customer = db.session.get(CustomerAccount, int(user_id))
    if customer:
        return customer

    worker = db.session.get(WorkerAccount, int(user_id))
    return worker


def seed_workers() -> None:
    if platform.workers:
        return

    workers = [
        WorkerFactory.create("plumber", 1, "John Smith", "Vilnius", 20, 4.5),
        WorkerFactory.create("mechanic", 2, "Mike Brown", "Kaunas", 25, 4.9),
        WorkerFactory.create("electrician", 3, "Anna White", "Vilnius", 22, 4.9),
        WorkerFactory.create("plumber", 4, "Laura Green", "Klaipeda", 18, 4.3),
        WorkerFactory.create("electrician", 5, "Tomas Black", "Kaunas", 24, 4.6),
        WorkerFactory.create("mechanic", 6, "Peter Stone", "Vilnius", 28, 4.8),
    ]

    for worker in workers:
        platform.add_worker(worker)


def get_seed_workers():
    return platform.search_workers()


def get_registered_workers():
    return WorkerAccount.query.all()


@app.route("/")
def home():
    seed_workers()

    location = request.args.get("location", "").strip()
    specialty = request.args.get("specialty", "").strip()

    seed_workers_list = get_seed_workers()
    registered_workers = get_registered_workers()

    workers = []

    for worker in seed_workers_list:
        workers.append(
            {
                "id": worker.person_id,
                "name": worker.name,
                "location": worker.location,
                "specialty": worker.specialty,
                "rate": worker.rate,
                "rating": worker.rating,
                "source": "seed"
            }
        )

    for worker in registered_workers:
        workers.append(
            {
                "id": worker.id,
                "name": worker.username,
                "location": worker.location,
                "specialty": worker.specialty,
                "rate": worker.hourly_rate,
                "rating": worker.rating,
                "source": "db"
            }
        )

    if location:
        workers = [
            worker for worker in workers
            if worker["location"].lower() == location.lower()
        ]

    if specialty:
        workers = [
            worker for worker in workers
            if worker["specialty"].lower() == specialty.lower()
        ]

    workers.sort(key=lambda item: (-item["rating"], item["rate"]))

    return render_template(
        "index.html",
        workers=workers,
        selected_location=location,
        selected_specialty=specialty,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        role = request.form.get("role", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not role or not username or not password:
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("register"))

        existing_customer = CustomerAccount.query.filter_by(
            username=username
        ).first()
        existing_worker = WorkerAccount.query.filter_by(
            username=username
        ).first()

        if existing_customer or existing_worker:
            flash("Username already exists.", "error")
            return redirect(url_for("register"))

        if role == "customer":
            user = CustomerAccount(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            flash("Customer registration successful.", "success")
            return redirect(url_for("login"))

        if role == "worker":
            specialty = request.form.get("specialty", "").strip()
            location = request.form.get("location", "").strip()
            hourly_rate = request.form.get("hourly_rate", "").strip()

            if not specialty or not location or not hourly_rate:
                flash("Worker must fill all worker fields.", "error")
                return redirect(url_for("register"))

            try:
                hourly_rate_value = float(hourly_rate)
            except ValueError:
                flash("Hourly rate must be a number.", "error")
                return redirect(url_for("register"))

            worker = WorkerAccount(
                username=username,
                specialty=specialty,
                location=location,
                hourly_rate=hourly_rate_value,
                rating=5.0
            )
            worker.set_password(password)

            db.session.add(worker)
            db.session.commit()

            flash("Worker registration successful.", "success")
            return redirect(url_for("login"))

        flash("Invalid role selected.", "error")
        return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if role == "customer":
            user = CustomerAccount.query.filter_by(username=username).first()
        elif role == "worker":
            user = WorkerAccount.query.filter_by(username=username).first()
        else:
            user = None

        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully.", "success")

            if role == "worker":
                return redirect(url_for("worker_dashboard"))

            return redirect(url_for("home"))

        flash("Invalid login details.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        new_username = request.form.get("username", "").strip()

        if not new_username:
            flash("Username cannot be empty.", "error")
            return redirect(url_for("profile"))

        existing_customer = CustomerAccount.query.filter_by(
            username=new_username
        ).first()
        existing_worker = WorkerAccount.query.filter_by(
            username=new_username
        ).first()

        same_customer = existing_customer and existing_customer.id != current_user.id
        same_worker = existing_worker and existing_worker.id != current_user.id

        if same_customer or same_worker:
            flash("That username is already taken.", "error")
            return redirect(url_for("profile"))

        current_user.username = new_username
        db.session.commit()

        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile"))

    request_count = 0
    if hasattr(current_user, "role") and current_user.role == "customer":
        request_count = ServiceRequestRecord.query.filter_by(
            customer_id=current_user.id
        ).count()

    return render_template("profile.html", request_count=request_count)


@app.route("/worker/<source>/<int:worker_id>", methods=["GET", "POST"])
@login_required
def worker_details(source: str, worker_id: int):
    if not hasattr(current_user, "role") or current_user.role != "customer":
        flash("Only customers can send requests.", "error")
        return redirect(url_for("home"))

    worker_data = None
    worker_account_id = None

    if source == "seed":
        for worker in platform.workers:
            if worker.person_id == worker_id:
                worker_data = {
                    "name": worker.name,
                    "location": worker.location,
                    "specialty": worker.specialty,
                    "rate": worker.rate,
                    "rating": worker.rating
                }
                break

    elif source == "db":
        worker = db.session.get(WorkerAccount, worker_id)
        if worker:
            worker_account_id = worker.id
            worker_data = {
                "name": worker.username,
                "location": worker.location,
                "specialty": worker.specialty,
                "rate": worker.hourly_rate,
                "rating": worker.rating
            }

    if worker_data is None:
        flash("Worker was not found.", "error")
        return redirect(url_for("home"))

    if request.method == "POST":
        problem_title = request.form.get("problem_title", "").strip()
        problem_description = request.form.get(
            "problem_description", ""
        ).strip()

        if not problem_title or not problem_description:
            flash("Please describe your problem.", "error")
            return redirect(
                url_for("worker_details", source=source, worker_id=worker_id)
            )

        request_count = ServiceRequestRecord.query.filter_by(
            customer_id=current_user.id
        ).count()

        if request_count >= 5:
            flash("You can store only 5 requests maximum.", "error")
            return redirect(url_for("requests_page"))

        new_request = ServiceRequestRecord(
            problem_title=problem_title,
            problem_description=problem_description,
            worker_name=worker_data["name"],
            worker_specialty=worker_data["specialty"],
            worker_location=worker_data["location"],
            hourly_rate=worker_data["rate"],
            rating=worker_data["rating"],
            customer_id=current_user.id,
            worker_account_id=worker_account_id
        )

        db.session.add(new_request)
        db.session.commit()

        flash("Your request was submitted successfully.", "success")
        return redirect(url_for("requests_page"))

    return render_template(
        "worker_details.html",
        worker=worker_data,
        source=source,
        worker_id=worker_id
    )


@app.route("/requests")
@login_required
def requests_page():
    if not hasattr(current_user, "role") or current_user.role != "customer":
        flash("Only customers have personal request history.", "error")
        return redirect(url_for("home"))

    requests_data = ServiceRequestRecord.query.filter_by(
        customer_id=current_user.id
    ).all()
    return render_template("requests.html", requests_data=requests_data)


@app.route("/worker_dashboard")
@login_required
def worker_dashboard():
    if not hasattr(current_user, "role") or current_user.role != "worker":
        flash("Only workers can open this page.", "error")
        return redirect(url_for("home"))

    requests_data = ServiceRequestRecord.query.filter_by(
        worker_account_id=current_user.id
    ).all()

    return render_template(
        "worker_dashboard.html",
        requests_data=requests_data
    )


@app.route("/delete_request/<int:request_id>", methods=["POST"])
@login_required
def delete_request(request_id: int):
    if not hasattr(current_user, "role") or current_user.role != "customer":
        flash("Only customers can delete requests.", "error")
        return redirect(url_for("home"))

    request_item = ServiceRequestRecord.query.filter_by(
        id=request_id,
        customer_id=current_user.id
    ).first()

    if request_item is None:
        flash("Request not found.", "error")
        return redirect(url_for("requests_page"))

    db.session.delete(request_item)
    db.session.commit()

    flash("Request deleted.", "success")
    return redirect(url_for("requests_page"))


if __name__ == "__main__":
    seed_workers()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
