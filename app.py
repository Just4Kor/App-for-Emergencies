from flask import Flask, render_template, request, redirect, url_for, flash

from services.platform import Platform
from factory.worker_factory import WorkerFactory

app = Flask(__name__)
app.secret_key = "coursework-secret-key"


platform = Platform()
service_requests = []


def seed_workers():
    """Load example workers into the platform once."""
    if platform.workers:
        return

    workers = [
        WorkerFactory.create(
            "plumber", 1, "Aleksas Aleksandravičius", "Vilnius", 20, 4.5
        ),
        WorkerFactory.create(
            "mechanic", 2, "Maikas Maiklasonas", "Kaunas", 25, 4.9
        ),
        WorkerFactory.create(
            "electrician", 3, "Ana Vilinija", "Vilnius", 22, 4.9
        ),
        WorkerFactory.create(
            "plumber", 4, "Laura Grazavaitė", "Klaipeda", 18, 4.3
        ),
        WorkerFactory.create(
            "electrician", 5, "Tomas Belingeris", "Kaunas", 24, 4.6
        ),
        WorkerFactory.create(
            "mechanic", 6, "Lukas Lukočiūnas", "Vilnius", 28, 4.8
        ),
    ]

    for worker in workers:
        platform.add_worker(worker)


def get_all_workers():
    """Return all workers sorted by backend logic."""
    return platform.search_workers()


def find_worker_by_id(worker_id: int):
    """Find one worker from the existing platform worker list."""
    for worker in platform.workers:
        if worker.person_id == worker_id:
            return worker
    return None


@app.route("/", methods=["GET"])
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


@app.route("/worker/<int:worker_id>", methods=["GET", "POST"])
def worker_details(worker_id: int):
    seed_workers()
    worker = find_worker_by_id(worker_id)

    if worker is None:
        flash("Worker was not found.", "error")
        return redirect(url_for("home"))

    if request.method == "POST":
        customer_name = request.form.get("customer_name", "").strip()
        customer_location = request.form.get("customer_location", "").strip()
        problem_title = request.form.get("problem_title", "").strip()
        problem_description = request.form.get(
            "problem_description", ""
        ).strip()

        if not customer_name or not customer_location:
            flash("Please enter your name and location.", "error")
            return redirect(url_for("worker_details", worker_id=worker_id))

        if not problem_title or not problem_description:
            flash("Please describe your problem.", "error")
            return redirect(url_for("worker_details", worker_id=worker_id))

        service_requests.append(
            {
                "customer_name": customer_name,
                "customer_location": customer_location,
                "worker_id": worker.person_id,
                "worker_name": worker.name,
                "worker_specialty": worker.specialty,
                "worker_location": worker.location,
                "hourly_rate": worker.rate,
                "rating": worker.rating,
                "problem_title": problem_title,
                "problem_description": problem_description,
            }
        )

        flash("Your request was submitted successfully.", "success")
        return redirect(url_for("requests_page"))

    return render_template("worker_details.html", worker=worker)


@app.route("/requests", methods=["GET"])
def requests_page():
    return render_template("requests.html", requests_data=service_requests)


if __name__ == "__main__":
    seed_workers()
    app.run(debug=True)
