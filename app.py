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


class UserAccount(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    requests = db.relationship(
        "ServiceRequestRecord",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class ServiceRequestRecord(db.Model):
    __tablename__ = "service_requests"

    id = db.Column(db.Integer, primary_key=True)
    problem_title = db.Column(db.String(120), nullable=False)
    problem_description = db.Column(db.Text, nullable=False)

    worker_id = db.Column(db.Integer, nullable=False)
    worker_name = db.Column(db.String(120), nullable=False)
    worker_specialty = db.Column(db.String(80), nullable=False)
    worker_location = db.Column(db.String(120), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Float, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return UserAccount.query.get(int(user_id))


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


def get_all_workers():
    return platform.search_workers()


def find_worker_by_id(worker_id: int):
    for worker in platform.workers:
        if worker.person_id == worker_id:
            return worker
    return None


@app.route("/")
def home():
    seed_workers()

    location = request.args.get("location", "").strip()
    specialty = request.args.get("specialty", "").strip()

    workers = get_all_workers()

    if location:
        workers = [
            worker for worker in workers
            if worker.location.lower() == location.lower()
        ]

    if specialty:
        workers = [
            worker for worker in workers
            if worker.specialty.lower() == specialty.lower()
        ]

    return render_template(
        "index.html",
        workers=workers,
        selected_location=location,
        selected_specialty=specialty,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Please fill in all fields.", "error")
            return redirect(url_for("register"))

        existing_user = UserAccount.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists.", "error")
            return redirect(url_for("register"))

        user = UserAccount(username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Registration successful. You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = UserAccount.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("home"))

        flash("Invalid username or password.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


@app.route("/worker/<int:worker_id>", methods=["GET", "POST"])
@login_required
def worker_details(worker_id: int):
    seed_workers()
    worker = find_worker_by_id(worker_id)

    if worker is None:
        flash("Worker was not found.", "error")
        return redirect(url_for("home"))

    if request.method == "POST":
        problem_title = request.form.get("problem_title", "").strip()
        problem_description = request.form.get(
            "problem_description", ""
        ).strip()

        if not problem_title or not problem_description:
            flash("Please describe your problem.", "error")
            return redirect(url_for("worker_details", worker_id=worker_id))

        request_count = ServiceRequestRecord.query.filter_by(
            user_id=current_user.id
        ).count()

        if request_count >= 5:
            flash("You can store only 5 requests maximum.", "error")
            return redirect(url_for("requests_page"))

        new_request = ServiceRequestRecord(
            problem_title=problem_title,
            problem_description=problem_description,
            worker_id=worker.person_id,
            worker_name=worker.name,
            worker_specialty=worker.specialty,
            worker_location=worker.location,
            hourly_rate=worker.rate,
            rating=worker.rating,
            user_id=current_user.id,
        )

        db.session.add(new_request)
        db.session.commit()

        flash("Your request was submitted successfully.", "success")
        return redirect(url_for("requests_page"))

    return render_template("worker_details.html", worker=worker)


@app.route("/requests")
@login_required
def requests_page():
    requests_data = ServiceRequestRecord.query.filter_by(
        user_id=current_user.id
    ).all()
    return render_template("requests.html", requests_data=requests_data)


@app.route("/delete_request/<int:request_id>", methods=["POST"])
@login_required
def delete_request(request_id: int):
    request_item = ServiceRequestRecord.query.filter_by(
        id=request_id,
        user_id=current_user.id
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
