from zone import Zone


class Connection:
    def __init__(self, from_dst: Zone, to_dst: Zone, capacity: int):
        self.name = from_dst.name + "-" + to_dst.name
        self.from_dst = from_dst
        self.to_dst = to_dst
        self.max_capacity = capacity
        self.drone_in = 0
        self.on_connection = False

    def get_current_capacity(self) -> int:
        return self.drone_in

    def has_space(self) -> bool:
        return self.drone_in < self.max_capacity
