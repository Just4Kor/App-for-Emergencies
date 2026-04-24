import os


WORKER_FILE_PATH = "data/workers.txt"


def load_workers_from_file():
    workers = []

    try:
        with open(WORKER_FILE_PATH, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(",")

                if len(parts) != 5:
                    continue

                name, specialty, location, hourly_rate, rating = parts

                workers.append(
                    {
                        "username": name.strip(),
                        "specialty": specialty.strip(),
                        "location": location.strip(),
                        "hourly_rate": float(hourly_rate),
                        "rating": float(rating),
                    }
                )

    except FileNotFoundError:
        return []

    return workers


def save_worker_to_file(worker):
    os.makedirs("data", exist_ok=True)

    with open(WORKER_FILE_PATH, "a", encoding="utf-8") as file:
        file.write(
            f"{worker.username},"
            f"{worker.specialty},"
            f"{worker.location},"
            f"{worker.hourly_rate},"
            f"{worker.rating}\n"
        )
