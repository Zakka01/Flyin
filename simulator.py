from collections import defaultdict
from typing import List

from connection import Connection
from drone import Drone
from zone import Zone


class Simulator:
    def __init__(
        self,
        drones: List[Drone],
        start_hub: Zone,
        end_hub: Zone,
        all_zones: List[Zone],
        connection_dict: dict,
    ):

        self.all_zones = all_zones
        self.drones = drones
        self.start = start_hub
        self.end = end_hub
        self.connections = connection_dict
        self.turns = 0
        self.is_running = True

    def is_all_delivered(self) -> bool:
        return all(drone.is_delivered() for drone in self.drones)

    def validate_moves(self, drones_moves: List) -> List[dict]:
        valid_moves = []

        planned_enters = defaultdict(int)
        planned_leaves = defaultdict(int)
        connection_count = defaultdict(int)

        drones_moves.sort(key=lambda m: int(m["drone"].id[1:]))

        for move in drones_moves:
            dst = move["dst"]
            current = move["current"]

            if isinstance(current, Zone):
                conn_info = self.get_connection(
                    current,
                    dst if not isinstance(dst, Connection) else dst.to_dst,
                )
                connection_name = (
                    conn_info["from"].name
                    + "-"
                    + conn_info["to"].name
                )
                connection_capacity = conn_info["connection_capacity"]

            else:
                connection_name = current.name
                connection_capacity = current.max_capacity

            if isinstance(dst, Connection):
                destination = dst.to_dst
            else:
                destination = dst

            future_occupancy = (
                destination.drone_in
                - planned_leaves[destination.name]
                + planned_enters[destination.name]
                + 1
            )

            if future_occupancy > destination.max_drones:
                continue

            if connection_count[connection_name] >= connection_capacity:
                continue

            valid_moves.append(move)

            planned_enters[destination.name] += 1
            connection_count[connection_name] += 1

            if isinstance(current, Zone):
                planned_leaves[current.name] += 1

        return valid_moves

    def get_connection(self, current: Zone, next: Zone) -> dict:
        from_dst = current
        to_dst = next  # default
        connection_capacity = 1  # default

        neighbors_of_current = self.connections[current.name]
        for neighbor in neighbors_of_current:
            if neighbor[0] == next:
                to_dst = neighbor[0]
                connection_capacity = neighbor[1]

        return {
            "from": from_dst,
            "to": to_dst,
            "connection_capacity": connection_capacity,
        }

    def apply_moves(self, valid_moves: List) -> None:

        for move in valid_moves:
            drone = move["drone"]
            dst = move["dst"]
            current = move["current"]
            move_type = move["type"]

            if move_type == "normal_move":
                drone.move()
                current.drone_in -= 1 if current.drone_in > 0 else 0
                dst.drone_in += 1

            elif move_type == "connection_enter":
                drone.move()
                dst.drone_in += 1
                current.drone_in -= 1 if current.drone_in > 0 else 0
                drone.on_connection = True

            elif move_type == "connection_exit":
                drone.move()
                current.drone_in -= 1 if current.drone_in > 0 else 0
                dst.drone_in += 1
                drone.on_connection = False

    def record_turn_output(self, valid_moves: List[dict]) -> None:
        if not valid_moves:
            return None

        turn_output = []
        for move in valid_moves:
            if not move.get("record"):
                continue

            drone_id = move["drone"].id
            dst = move["dst"]
            destination_name = dst.name

            turn_output.append(f"{drone_id}-{destination_name}")

        if turn_output:
            output_line = " ".join(turn_output)
            print(output_line)
            self.turns += 1

    def play(self) -> int:

        drones_moves = []

        # for the render (pygame) to stop the simulation
        if self.is_all_delivered():
            self.is_running = False

        for drone in self.drones:
            if drone.is_delivered():
                continue

            current = drone.current_zone()

            if isinstance(current, Connection):
                drones_moves.append(
                    {
                        "current": current,
                        "drone": drone,
                        "dst": current.to_dst,
                        "type": "connection_exit",
                        "record": True,
                    }
                )

            elif drone.can_move():
                next_item = drone.next_zone()

                if isinstance(next_item, Connection):
                    drones_moves.append(
                        {
                            "current": current,
                            "drone": drone,
                            "dst": next_item,
                            "type": "connection_enter",
                            "record": True,
                        }
                    )

                else:
                    drones_moves.append(
                        {
                            "current": current,
                            "drone": drone,
                            "dst": next_item,
                            "type": "normal_move",
                            "record": True,
                        }
                    )

        valid_moves = self.validate_moves(drones_moves)
        self.apply_moves(valid_moves)
        self.record_turn_output(valid_moves)

        return self.turns
