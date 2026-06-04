from drone import Drone
from graph import Graph
from parsing import Parser
from render import Render
from simulator import Simulator
from zone import Zone
from typing import List, Any


def get_drones_nb(config: dict) -> int | Any:
    return config["nb_drones"]


def assign_path_to_drone(nb_drones: int, all_paths: List) -> List:
    try:
        drones = []
        selected_paths = all_paths[:2] if len(all_paths) >= 2 \
            else all_paths

        for i in range(nb_drones):
            path = selected_paths[i % len(selected_paths)]["path"]
            drone = Drone(f"D{i + 1}", path)
            drones.append(drone)
    except Exception as e:
        print(f"Error assigning paths to drones: {e}")
        exit(0)

    return drones


def main() -> None:
    try:
        import importlib
        importlib.import_module("webcolors")
        importlib.import_module("pygame")
        importlib.import_module("flake8")
        importlib.import_module("mypy")
    except Exception as e:
        raise ImportError(f"Missing dependency: {e}")
        exit(1)

    parser = Parser()
    config = parser.parsing_config()

    no_render = config.get("no_render", False)

    nb_drones = get_drones_nb(config)
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

    drones = assign_path_to_drone(nb_drones, all_paths)
    connection_dct = graph.build_connection_dict()
    simulator = Simulator(
        drones, graph.start_hub, graph.end_hub, all_zones, connection_dct
    )

    zones = graph.get_all_zones()
    connections = graph.build_connection_dict()
    render = Render(zones, connections, graph, drones, simulator)

    if no_render:
        while not simulator.is_all_delivered():
            simulator.play()
    else:
        render.play()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
