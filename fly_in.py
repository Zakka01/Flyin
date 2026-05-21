from typing import List

from connection import Connection
from drone import Drone
from graph import Graph
from parsing import Parser
from render import Render
from simulator import Simulator
from zone import Zone


class Main:
    def get_drones_nb(self, config) -> int:
        return config["nb_drones"]

    def assign_path_to_drone(self, nb_drones: int, all_paths: List) -> List:
        try:
            drones = []
            selected_paths = all_paths[:2] if len(all_paths) >= 2 else all_paths

            # for i, p in enumerate(selected_paths, 1):
            for i, p in enumerate(selected_paths, 1):
                path = p["path"]
                cost = p["cost"]

                lst = []
                for v in path:
                    # Skip Connection objects
                    if isinstance(v, Connection):
                        continue

                    # Check priority
                    if v.is_zone_priority():
                        # Yellow with star
                        lst.append(f"\033[93m★ {v.name}\033[0m")
                    else:
                        # Green
                        lst.append(f"\033[92m{v.name}\033[0m")

                print(f"Path {i}: {' >> '.join(lst)}")
                print(f"Cost: {cost}\n")

            for i in range(nb_drones):
                path = selected_paths[i % len(selected_paths)]["path"]
                drone = Drone(f"D{i + 1}", path)
                drones.append(drone)
        except Exception as e:
            print(f"Error assigning paths to drones: {e}")
            exit(0)

        return drones

    def main(self) -> None:
        parser = Parser()
        config = parser.parsing_config()

        nb_drones = self.get_drones_nb(config)
        graph = Graph(config)

        all_zones = graph.get_all_zones()
        all_paths = graph.find_all_paths()

        all_paths = sorted(
            all_paths,
            key=lambda path: (
                path["cost"],
                not any(
                    zone.is_zone_priority()
                    for zone in path["path"]
                    if isinstance(zone, Zone)
                ),
            ),
        )

        drones = self.assign_path_to_drone(nb_drones, all_paths)
        connection_dct = graph.build_connection_dict()
        simulator = Simulator(
            drones, graph.start_hub, graph.end_hub, all_zones, connection_dct
        )

        zones = graph.get_all_zones()
        connections = graph.build_connection_dict()
        render = Render(zones, connections, graph, drones, simulator)
        render.play()


if __name__ == "__main__":
    main = Main()
    main.main()
