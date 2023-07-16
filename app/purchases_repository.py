from attrs import define


@define
class Purchase:
    user_id: int = 0
    flower_id: int = 0
    id: int = 0


class PurchasesRepository:
    purchases: list[Purchase]

    def __init__(self):
        self.purchases = []

    # необходимые методы сюда
    def save(self, purchase: Purchase):
        purchase.id = len(self.purchases) + 1
        self.purchases.append(purchase)
    def get_all(self) -> list[Purchase]:
        return self.purchases

    def get_all_purchases_by_user_id(self, user_id: int) -> list[Purchase]:
        return [purchase for purchase in self.purchases if purchase.user_id == user_id]

    # конец решения
