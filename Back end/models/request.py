class ServiceRequest:
    def __init__(self, request_id, user, worker, title, description):
        self.request_id = request_id
        self.user = user
        self.worker = worker
        self.title = title
        self.description = description
        self.status = "Pending"

    def accept(self):
        self.status = "Accepted"

    def deny(self):
        self.status = "Denied"
