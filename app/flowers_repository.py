from attrs import define


@define
class Flower:
    name: str
    count: int
    cost: int
    id: int = 0


class FlowersRepository:
    flowers: list[Flower]

    def __init__(self):
        self.flowers = []

    # необходимые методы сюда

    def get_all(self) -> list[Flower]:
        return self.flowers

    def get_one(self, id: int) -> Flower:
        for flower in self.flowers:
            if flower.id == id:
                return flower
        return None
    def minus_flower(self, id:int):
        for flower in self.flowers:
            if flower.id == id and flower.count != 0:
                flower.count -= 1

    def save(self, flower: Flower):
        flower.id = len(self.flowers) + 1
        self.flowers.append(flower)
