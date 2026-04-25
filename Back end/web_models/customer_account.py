from web_models.account import AccountView


class CustomerView(AccountView):
    def __init__(self, customer):
        super().__init__(customer)
        self.city = customer.city
