from collections import deque
from typing import List, Any

from connection import Connection
from zone import Zone


class Graph:
    def __init__(self, config: dict):
        self.config = config
        self.all_zones = self.get_all_zones()
        self.zone_lookup = {z.name: z for z in self.all_zones}
        self.start_hub = self.zone_lookup[config["start_hub"]["name"]]
        self.end_hub = self.zone_lookup[config["end_hub"]["name"]]
        self.connection_dict = self.build_connection_dict()
        self.paths: List[dict[str, Any]] = []

    def get_all_zones(self) -> List[Zone]:

        all_zones = []
        try:
            if "start_hub" in self.config:
                all_zones.append(Zone(self.config["start_hub"]))

            if "end_hub" in self.config:
                all_zones.append(Zone(self.config["end_hub"]))

            if "hub" in self.config:
                for hub in self.config["hub"]:
                    all_zones.append(Zone(hub))

            seen_names = set()
            dups_names = set()

            seen_coors = set()
            dups_coors = set()

            for zone in all_zones:
                coordinates = (zone.y, zone.x)

                if zone.name in seen_names:
                    dups_names.add(zone.name)

                if coordinates in seen_coors:
                    dups_coors.add(coordinates)

                seen_coors.add(coordinates)
                seen_names.add(zone.name)

            if dups_names:
                raise ValueError("Can't have two duplicated zones name")
            if dups_coors:
                raise ValueError(
                    "Can't have two zones with "
                    "the same Coordinates"
                )

        except ValueError as e:
            print(f"ERROR: {e}")
            exit(0)

        return all_zones

    def build_connection_dict(self) -> dict:

        connection_dict: dict[str, list] = {}
        for zone in self.all_zones:
            connection_dict[zone.name] = []

        for c in self.config["connection"]:
            from_name = c["from"]
            to_name = c["to"]
            capacity = c.get("max_link_capacity", 1)

            to_zone = self.zone_lookup[to_name]
            from_zone = self.zone_lookup[from_name]

            connection_dict[from_name].append((to_zone, capacity))
            connection_dict[to_name].append((from_zone, capacity))

        return connection_dict

    def build_paths(self, path: List) -> None:
        cost = 0
        for p in path[1:]:
            if not isinstance(p, Connection):
                cost += p.it_cost()
        self.paths.append({"path": path, "cost": cost})

    def find_all_paths(self) -> List[dict]:

        queue = deque([(self.start_hub, [self.start_hub])])

        while queue:
            current_zone, path_so_far = queue.popleft()

            # build path when current is end and continue find other paths
            if current_zone.name == self.end_hub.name:
                self.build_paths(path_so_far)
                continue

            neighbors = self.connection_dict[current_zone.name]
            for neighbor, capacity in neighbors:
                if neighbor in path_so_far:
                    continue

                if neighbor.is_zone_blocked():
                    continue

                if neighbor.is_zone_restricted():
                    connection = Connection(current_zone, neighbor, capacity)
                    new_path = path_so_far + [connection] + [neighbor]
                    queue.append((neighbor, new_path))

                else:
                    if neighbor.is_zone_priority():
                        new_path = path_so_far + [neighbor]
                        queue.appendleft((neighbor, new_path))
                    else:
                        new_path = path_so_far + [neighbor]
                        queue.append((neighbor, new_path))

        return self.paths
