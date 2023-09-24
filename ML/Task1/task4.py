class BankCard:
    def __init__(self, total_sum):
        self.total_sum = total_sum

    def __repr__(self):
        return "To learn the balance you should put the money " \
               "on the card, spent some money or get the bank data. " \
               "The last procedure is not free and costs 1 dollar."

    def __call__(self, *args, **kwargs):
        cost = args[0]
        if self.total_sum - cost < 0:
            raise ValueError
        else:
            self.total_sum -= cost
            print("You spent {} dollars. {} dollars are left.".format(cost, self.total_sum))

    @property
    def balance(self):
        if self.total_sum - 1 < 0:
            print("Not enough money to learn the balance.")
            raise ValueError
        else:
            self.total_sum -= 1
            return self.total_sum

    def put(self, sum_put):
        self.total_sum += sum_put
        print("You put {} dollars. {} dollars are left.".format(sum_put, self.total_sum))


def test_bank_card():
    a = BankCard(100)
    assert a.total_sum == 100
    assert a.__repr__() == "To learn the balance you should put the money on the card, spent some money or get the bank data. The last procedure is not free and costs 1 dollar."
    a(50)
    assert a.total_sum == 50
    assert a.balance == 49
    try:
        a(50)
    except ValueError:
        pass
    a.put(30)
    assert a.balance == 78


if __name__ == "__main__":
    test_bank_card()
