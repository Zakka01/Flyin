class Zone:
    def __init__(self, config: dict) -> None:
        self.name = config["name"]
        self.y = config["y"]
        self.x = config["x"]
        self.zone_type = config["zone"]
        self.color = config["color"]
        self.max_drones = config["max_drones"]
        self.drone_in = 0

    def is_zone_blocked(self) -> bool:
        return self.zone_type == "blocked"

    def is_zone_restricted(self) -> bool:
        return self.zone_type == "restricted"

    def is_zone_normal(self) -> bool:
        return self.zone_type == "normal"

    def is_zone_priority(self) -> bool:
        return self.zone_type == "priority"

    def it_cost(self) -> int:
        if self.is_zone_restricted():
            return 2
        return 1

    def get_max_drones(self) -> int:
        return self.max_drones

    def has_space(self) -> bool:
        return self.drone_in < self.max_drones
