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
from werkzeug.security import check_password_hash, generate_password_hash

from worker_create import WorkerFactory
from models.person import ValidationError
from models.rating import WorkerRating
from services.platform import Platform
from services.rating_service import RatingService

app = Flask(__name__)
app.config["SECRET_KEY"] = "coursework-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///emergency_services.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

platform = Platform()
rating_service = RatingService()

SPECIALTIES = [
    "Plumber",
    "Electrician",
    "Mechanic",
    "Carpenter",
    "Painter",
    "Locksmith",
    "HVAC Technician",
]

LOCATIONS = [
    "Vilnius",
    "Kaunas",
    "Klaipėda",
    "Šiauliai",
    "Panevėžys",
    "Alytus",
    "Marijampolė",
    "Utena",
]


class CustomerAccount(UserMixin, db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(120), nullable=False, default="Unknown")

    requests = db.relationship(
        "ServiceRequestRecord",
        backref="customer",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="ServiceRequestRecord.created_at",
    )

    given_ratings = db.relationship(
        "WorkerRatingRecord",
        backref="customer",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def get_id(self) -> str:
        return f"customer:{self.id}"

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
        cascade="all, delete-orphan",
    )

    received_ratings = db.relationship(
        "WorkerRatingRecord",
        backref="worker",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def get_id(self) -> str:
        return f"worker:{self.id}"

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
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False,
    )

    worker_account_id = db.Column(
        db.Integer,
        db.ForeignKey("worker_accounts.id"),
        nullable=True,
    )


class WorkerRatingRecord(db.Model):
    __tablename__ = "worker_ratings"

    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(300), nullable=True)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False,
    )

    worker_id = db.Column(
        db.Integer,
        db.ForeignKey("worker_accounts.id"),
        nullable=False,
    )

    __table_args__ = (
        db.UniqueConstraint(
            "customer_id",
            "worker_id",
            name="unique_customer_worker_rating",
        ),
    )


@login_manager.user_loader
def load_user(user_id: str):
    try:
        role, raw_id = user_id.split(":", 1)
        numeric_id = int(raw_id)
    except (ValueError, AttributeError):
        return None

    if role == "customer":
        return db.session.get(CustomerAccount, numeric_id)

    if role == "worker":
        return db.session.get(WorkerAccount, numeric_id)

    return None


def seed_workers() -> None:
    if platform.workers:
        return

    workers = [
        WorkerFactory.create("Plumber", 1, "John Smith", "Vilnius", 20, 4.5),
        WorkerFactory.create("Mechanic", 2, "Mike Brown", "Kaunas", 25, 4.9),
        WorkerFactory.create("Electrician", 3, "Anna White", "Vilnius", 22, 4.9),
        WorkerFactory.create("Carpenter", 4, "Laura Green", "Klaipeda", 18, 4.3),
        WorkerFactory.create("Painter", 5, "Tomas Black", "Siauliai", 24, 4.6),
        WorkerFactory.create("Locksmith", 6, "Peter Stone", "Panevezys", 28, 4.8),
    ]

    for worker in workers:
        platform.add_worker(worker)


def get_seed_workers():
    return platform.search_workers()


def get_registered_workers():
    return WorkerAccount.query.all()


def refresh_worker_rating(worker: WorkerAccount) -> None:
    rating_service_local = RatingService()

    records = WorkerRatingRecord.query.filter_by(worker_id=worker.id).all()

    for record in records:
        oop_rating = WorkerRating(
            rating_id=record.id,
            customer_id=record.customer_id,
            worker_id=record.worker_id,
            score=record.score,
            comment=record.comment or "",
            created_at=record.created_at.isoformat(),
        )
        rating_service_local.add_rating(oop_rating)

    average = rating_service_local.get_average_rating(worker.id)
    worker.rating = round(average, 2) if average > 0 else 5.0
    db.session.commit()


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
                "source": "seed",
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
                "source": "db",
            }
        )

    if location:
        workers = [
            worker
            for worker in workers
            if worker["location"].lower() == location.lower()
        ]

    if specialty:
        workers = [
            worker
            for worker in workers
            if worker["specialty"].lower() == specialty.lower()
        ]

    workers.sort(key=lambda item: (-item["rating"], item["rate"]))

    return render_template(
        "index.html",
        workers=workers,
        selected_location=location,
        selected_specialty=specialty,
        specialties=SPECIALTIES,
        locations=LOCATIONS,
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

        existing_customer = CustomerAccount.query.filter_by(username=username).first()
        existing_worker = WorkerAccount.query.filter_by(username=username).first()

        if existing_customer or existing_worker:
            flash("Username already exists.", "error")
            return redirect(url_for("register"))

        if role == "customer":
            city = request.form.get("city", "").strip()

            if not city:
                flash("Please enter your city.", "error")
                return redirect(url_for("register"))

            if city not in LOCATIONS:
                flash("Please choose a valid city.", "error")
                return redirect(url_for("register"))

            user = CustomerAccount(username=username, city=city)
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

            if specialty not in SPECIALTIES:
                flash("Invalid specialty selected.", "error")
                return redirect(url_for("register"))

            if location not in LOCATIONS:
                flash("Invalid location selected.", "error")
                return redirect(url_for("register"))

            try:
                hourly_rate_value = float(hourly_rate)
            except ValueError:
                flash("Hourly rate must be a number.", "error")
                return redirect(url_for("register"))

            if hourly_rate_value <= 0:
                flash("Hourly rate must be greater than 0.", "error")
                return redirect(url_for("register"))

            worker = WorkerAccount(
                username=username,
                specialty=specialty,
                location=location,
                hourly_rate=hourly_rate_value,
                rating=5.0,
            )
            worker.set_password(password)

            db.session.add(worker)
            db.session.commit()

            flash("Worker registration successful.", "success")
            return redirect(url_for("login"))

        flash("Invalid role selected.", "error")
        return redirect(url_for("register"))

    return render_template(
        "register.html",
        specialties=SPECIALTIES,
        locations=LOCATIONS,
    )


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

        existing_customer = CustomerAccount.query.filter_by(username=new_username).first()
        existing_worker = WorkerAccount.query.filter_by(username=new_username).first()

        username_taken_by_other_customer = (
            existing_customer is not None and
            not (
                current_user.role == "customer" and
                existing_customer.id == current_user.id
            )
        )

        username_taken_by_other_worker = (
            existing_worker is not None and
            not (
                current_user.role == "worker" and
                existing_worker.id == current_user.id
            )
        )

        if username_taken_by_other_customer or username_taken_by_other_worker:
            flash("That username is already taken.", "error")
            return redirect(url_for("profile"))

        current_user.username = new_username

        if current_user.role == "customer":
            new_city = request.form.get("city", "").strip()
            if not new_city:
                flash("City cannot be empty.", "error")
                return redirect(url_for("profile"))
            if new_city not in LOCATIONS:
                flash("Please choose a valid city.", "error")
                return redirect(url_for("profile"))
            current_user.city = new_city

        if current_user.role == "worker":
            new_location = request.form.get("location", "").strip()
            new_hourly_rate = request.form.get("hourly_rate", "").strip()

            if not new_location:
                flash("Location cannot be empty.", "error")
                return redirect(url_for("profile"))

            if new_location not in LOCATIONS:
                flash("Please choose a valid location.", "error")
                return redirect(url_for("profile"))

            try:
                rate_value = float(new_hourly_rate)
            except ValueError:
                flash("Hourly rate must be a number.", "error")
                return redirect(url_for("profile"))

            if rate_value <= 0:
                flash("Hourly rate must be greater than 0.", "error")
                return redirect(url_for("profile"))

            current_user.location = new_location
            current_user.hourly_rate = rate_value

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile"))

    request_count = 0
    if current_user.role == "customer":
        request_count = ServiceRequestRecord.query.filter_by(
            customer_id=current_user.id
        ).count()

    ratings_count = 0
    if current_user.role == "worker":
        ratings_count = WorkerRatingRecord.query.filter_by(
            worker_id=current_user.id
        ).count()

    return render_template(
        "profile.html",
        request_count=request_count,
        ratings_count=ratings_count,
        locations=LOCATIONS,
    )


@app.route("/worker/<source>/<int:worker_id>", methods=["GET", "POST"])
@login_required
def worker_details(source: str, worker_id: int):
    if current_user.role != "customer":
        flash("Only customers can send requests.", "error")
        return redirect(url_for("home"))

    worker_data = None
    worker_account_id = None
    already_rated = False
    existing_rating = None

    if source == "seed":
        for worker in platform.workers:
            if worker.person_id == worker_id:
                worker_data = {
                    "name": worker.name,
                    "location": worker.location,
                    "specialty": worker.specialty,
                    "rate": worker.rate,
                    "rating": worker.rating,
                    "source": "seed",
                }
                break

    elif source == "db":
        worker = db.session.get(WorkerAccount, worker_id)
        if worker is not None:
            worker_account_id = worker.id
            existing_rating = WorkerRatingRecord.query.filter_by(
                customer_id=current_user.id,
                worker_id=worker.id,
            ).first()
            already_rated = existing_rating is not None

            worker_data = {
                "name": worker.username,
                "location": worker.location,
                "specialty": worker.specialty,
                "rate": worker.hourly_rate,
                "rating": worker.rating,
                "source": "db",
            }

    if worker_data is None:
        flash("Worker was not found.", "error")
        return redirect(url_for("home"))

    if request.method == "POST":
        action = request.form.get("action", "").strip()

        if action == "create_request":
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
                oldest_request = ServiceRequestRecord.query.filter_by(
                    customer_id=current_user.id
                ).order_by(ServiceRequestRecord.created_at.asc()).first()

                if oldest_request is not None:
                    db.session.delete(oldest_request)
                    db.session.commit()

            new_request = ServiceRequestRecord(
                problem_title=problem_title,
                problem_description=problem_description,
                worker_name=worker_data["name"],
                worker_specialty=worker_data["specialty"],
                worker_location=worker_data["location"],
                hourly_rate=worker_data["rate"],
                rating=worker_data["rating"],
                customer_id=current_user.id,
                worker_account_id=worker_account_id,
            )

            db.session.add(new_request)
            db.session.commit()

            flash(
                "Request submitted successfully. If you already had 5 requests, "
                "the oldest one was removed.",
                "success",
            )
            return redirect(url_for("requests_page"))

        if action == "rate_worker":
            if source != "db" or worker_account_id is None:
                flash("Only registered workers can be rated.", "error")
                return redirect(
                    url_for("worker_details", source=source, worker_id=worker_id)
                )

            score_raw = request.form.get("score", "").strip()
            comment = request.form.get("comment", "").strip()
            next_rating_id = WorkerRatingRecord.query.count() + 1

            try:
                oop_rating = WorkerRating(
                    rating_id=next_rating_id,
                    customer_id=current_user.id,
                    worker_id=worker_account_id,
                    score=int(score_raw),
                    comment=comment,
                )
            except (ValueError, ValidationError) as error:
                flash(str(error), "error")
                return redirect(
                    url_for("worker_details", source=source, worker_id=worker_id)
                )

            worker = db.session.get(WorkerAccount, worker_account_id)

            existing_rating = WorkerRatingRecord.query.filter_by(
                customer_id=current_user.id,
                worker_id=worker_account_id,
            ).first()

            if existing_rating is None:
                rating_item = WorkerRatingRecord(
                    score=oop_rating.score,
                    comment=oop_rating.comment,
                    customer_id=oop_rating.customer_id,
                    worker_id=oop_rating.worker_id,
                )
                db.session.add(rating_item)
            else:
                existing_rating.score = oop_rating.score
                existing_rating.comment = oop_rating.comment
                existing_rating.created_at = datetime.utcnow()

            db.session.commit()
            refresh_worker_rating(worker)

            flash("Rating saved successfully.", "success")
            return redirect(
                url_for("worker_details", source=source, worker_id=worker_id)
            )

    ratings = []
    if worker_account_id is not None:
        records = WorkerRatingRecord.query.filter_by(
            worker_id=worker_account_id
        ).order_by(WorkerRatingRecord.created_at.desc()).all()

        for record in records:
            ratings.append(
                WorkerRating(
                    rating_id=record.id,
                    customer_id=record.customer_id,
                    worker_id=record.worker_id,
                    score=record.score,
                    comment=record.comment or "",
                    created_at=record.created_at.isoformat(),
                )
            )

    return render_template(
        "worker_details.html",
        worker=worker_data,
        source=source,
        worker_id=worker_id,
        worker_account_id=worker_account_id,
        already_rated=already_rated,
        existing_rating=existing_rating,
        ratings=ratings,
    )


@app.route("/requests")
@login_required
def requests_page():
    if current_user.role != "customer":
        flash("Only customers have personal request history.", "error")
        return redirect(url_for("home"))

    requests_data = ServiceRequestRecord.query.filter_by(
        customer_id=current_user.id
    ).order_by(ServiceRequestRecord.created_at.desc()).all()

    return render_template("requests.html", requests_data=requests_data)


@app.route("/worker_dashboard")
@login_required
def worker_dashboard():
    if current_user.role != "worker":
        flash("Only workers can open this page.", "error")
        return redirect(url_for("home"))

    requests_data = ServiceRequestRecord.query.filter_by(
        worker_account_id=current_user.id
    ).order_by(ServiceRequestRecord.created_at.desc()).all()

    rating_records = WorkerRatingRecord.query.filter_by(
        worker_id=current_user.id
    ).order_by(WorkerRatingRecord.created_at.desc()).all()

    ratings = []
    for record in rating_records:
        ratings.append(
            WorkerRating(
                rating_id=record.id,
                customer_id=record.customer_id,
                worker_id=record.worker_id,
                score=record.score,
                comment=record.comment or "",
                created_at=record.created_at.isoformat(),
            )
        )

    return render_template(
        "worker_dashboard.html",
        requests_data=requests_data,
        ratings=ratings,
    )


@app.route("/delete_request/<int:request_id>", methods=["POST"])
@login_required
def delete_request(request_id: int):
    if current_user.role != "customer":
        flash("Only customers can delete requests.", "error")
        return redirect(url_for("home"))

    request_item = ServiceRequestRecord.query.filter_by(
        id=request_id,
        customer_id=current_user.id,
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
