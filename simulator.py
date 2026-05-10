from drone import Drone
from zone import Zone
from connection import Connection
from typing import List
from collections import defaultdict


class Simulator:

    def __init__(self, drones: List[Drone],
                 start_hub: Zone,
                 end_hub: Zone,
                 all_zones: List[Zone],
                 connection_dict: dict):

        self.all_zones = all_zones
        self.drones = drones
        self.start = start_hub
        self.end = end_hub
        self.connections = connection_dict
        self.output = []
        self.turns = 0
        self.is_running = True

    def is_all_delivered(self) -> bool:
        return all(drone.is_delivered() for drone in self.drones)

    def validate_moves(self, drones_moves: List):
        valid_moves = []
        dst_count = defaultdict(int)
        connection_count = defaultdict(int)

        drones_moves.sort(key=lambda m: int(m["drone"].id[1:]))

        for move in drones_moves:
            dst = move["dst"]
            dst_name = dst.name
            current_zone = move["drone"].current_zone()

            if isinstance(current_zone, Zone):
                connection_info = self.get_connection(current_zone, dst)
                connection_capacity = connection_info["connection_capacity"]
                connection_name = connection_info["from"].name + "-" + \
                    connection_info["to"].name
            else:
                connection_capacity = current_zone.max_capacity
                connection_name = current_zone.name

            if isinstance(dst, Connection):
                max_capacity = dst.max_capacity
            else:
                max_capacity = dst.max_drones

            drone_leaving = 0
            if current_zone != dst:
                drone_leaving += 1

            current_capacity = dst.drone_in
            available_slots = max_capacity - current_capacity + drone_leaving

            if dst_count[dst_name] < available_slots and \
               connection_count[connection_name] < connection_capacity and \
               connection_count[connection_name] < max_capacity:

                valid_moves.append(move)
                dst_count[dst_name] += 1
                connection_count[connection_name] += 1

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
            "connection_capacity": connection_capacity
        }

    def apply_moves(self, valid_moves: List):
        for move in valid_moves:
            drone = move["drone"]
            dst = move["dst"]
            current = move["current"]
            move_type = move["type"]

            if move_type == "normal_move":
                drone.move(flag=False)
                current.drone_in -= 1 if current.drone_in > 0 else 0
                dst.drone_in += 1

            elif move_type == "connection_enter":
                drone.move(flag=True)
                dst.drone_in += 1
                current.drone_in -= 1 if current.drone_in > 0 else 0
                drone.on_connection = True

            elif move_type == "connection_exit":
                drone.move(flag=False)
                current.drone_in -= 1 if current.drone_in > 0 else 0
                dst.drone_in += 1
                drone.on_connection = False

    def record_turn_output(self, valid_moves: List[dict]):
        if not valid_moves:
            return

        turn_output = []
        for move in valid_moves:
            if not move.get("record"):
                continue

            drone_id = move["drone"].id
            dst = move["dst"]

            if isinstance(dst, Connection):
                destination_name = dst.name
            else:
                destination_name = dst.name

            turn_output.append(f"{drone_id}-{destination_name}")

        if turn_output:
            output_line = " ".join(turn_output)
            self.output.append(output_line)
            print(output_line)

        return output_line

    def play(self) -> int:
        output = []

        if self.is_all_delivered():
            self.is_running = False

        drones_moves = []

        for drone in self.drones:
            if drone.is_delivered():
                continue

            current = drone.current_zone()

            if isinstance(current, Connection):
                drones_moves.append({
                    "current": current,
                    "drone": drone,
                    "dst": current.to_dst,
                    "type": "connection_exit",
                    "record": True
                })

            elif drone.can_move():
                next_item = drone.next_zone()

                if isinstance(next_item, Connection):
                    drones_moves.append({
                        "current": current,
                        "drone": drone,
                        "dst": next_item,
                        "type": "connection_enter",
                        "record": True
                    })

                else:
                    drones_moves.append({
                        "current": current,
                        "drone": drone,
                        "dst": next_item,
                        "type": "normal_move",
                        "record": True
                    })

        valid_moves = self.validate_moves(drones_moves)
        self.apply_moves(valid_moves)
        output.append(self.record_turn_output(valid_moves))
        self.turns += 1

        return self.turns
