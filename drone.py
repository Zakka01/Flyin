from typing import List

from connection import Connection
from zone import Zone


class Drone:
    def __init__(self, id: str, path: List[Zone]):
        self.id = id
        self.path = path
        self.current_pos = 0

    def current_zone(self) -> Zone:
        return self.path[self.current_pos]

    def next_zone(self) -> Zone:
        return self.path[self.current_pos + 1]

    def next_of_next_zone(self) -> Zone:
        return self.path[self.current_pos + 2]

    def deliver(self):
        self.status = "delivered"

    def move(self, flag: bool = False):
        if flag:
            self.status = "waiting"
        self.current_pos += 1
        self.status = "moving"

    def is_delivered(self) -> bool:
        return self.current_pos >= len(self.path) - 1

    def can_move(self) -> bool:
        next_pos = self.current_pos + 1
        if next_pos >= len(self.path):
            return False
        return True

    def on_connection(self, current_zone: Zone):
        return isinstance(current_zone, Connection)

    def on_zone(self, current_zone: Zone):
        return isinstance(current_zone, Zone)
