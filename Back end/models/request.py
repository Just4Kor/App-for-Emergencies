from models.request_status import RequestStatus


class ServiceRequest:from models.request_status import RequestStatus


class ServiceRequest:
    def __init__(
        self,
        request_id,
        title,
        description,
        address,
        status,
        customer_id,
        worker_id,
    ):
        self.id = str(request_id)
        self.title = title
        self.description = description
        self.address = address
        self.status = status or RequestStatus.PENDING
        self.customer_id = str(customer_id)
        self.worker_id = str(worker_id)

    def accept(self):
        self.status = RequestStatus.ACCEPTED

    def deny(self):
        self.status = RequestStatus.DENIED
    def __init__(
        self,
        request_id,
        title,
        description,
        address,
        status,
        customer_id,
        worker_id,
    ):
        self.id = str(request_id)
        self.title = title
        self.description = description
        self.address = address
        self.status = status or RequestStatus.PENDING
        self.customer_id = str(customer_id)
        self.worker_id = str(worker_id)

    def accept(self):
        self.status = RequestStatus.ACCEPTED

    def deny(self):
        self.status = RequestStatus.DENIED
