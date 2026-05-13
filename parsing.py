import sys
import webcolors


class Parser:
    def __init__(self) -> None:
        self.config: dict = {}
        self.connection_hubs: list = []

    def parse_connection(self, value: str) -> dict:
        max_link_capacity = 1

        if "[" in value:
            dist, metadata = value.strip().split(" ", 1)
            metadata = metadata.strip()

            if not (metadata.startswith("[") and metadata.endswith("]")):
                raise ValueError("Invalid metadata")

            metadata = metadata.strip("[]").strip()
            if "=" not in metadata:
                raise ValueError("Invalid metadata")

            key, value = metadata.split("=", 1)
            if key != "max_link_capacity":
                raise ValueError("Invalid Metadata for connection")

            max_link_capacity = int(value)
        else:
            dist = value

        if "-" not in dist:
            raise ValueError("Invalid connection format")
        from_dist, to_dist = dist.strip().split("-", 1)

        connection = {from_dist.strip(), to_dist.strip()}
        if connection in self.connection_hubs:
            raise ValueError("Duplicate connection")
        self.connection_hubs.append(connection)

        return {
            "from": from_dist.strip(),
            "to": to_dist.strip(),
            "max_link_capacity": max_link_capacity
        }

    def parse_hub(self, value: str) -> dict:
        try:
            name, x, other = value.strip().split(maxsplit=2)
            name, x, other = name.strip(), x.strip(), other.strip()
        except Exception:
            raise Exception("Invalid Config - Not enough values")

        if "-" in name or " " in name:
            raise ValueError(f"Invalid zone name '{name}', Zone names cannot contain '-'")

        metadata_dict = {}
        y = 0

        # Check if there is metadata
        if " " in other:
            y, metadata = other.split(" ", 1)
            y, metadata = y.strip(), metadata.strip()

            if not metadata.startswith("[") or not metadata.endswith("]"):
                raise ValueError(f"Invalid Metadata '{metadata}'")

            if "=" not in metadata:
                raise ValueError("Invalid Metadata format")

            metadata = metadata.strip("[]")
            pairs = metadata.split()

            for pair in pairs:
                # validate metadata format
                if "=" not in pair:
                    raise ValueError("Invalid Metadata format")
                key, value = pair.split("=", 1)

                # validate metadata keys
                if key not in ["zone", "color", "max_drones"]:
                    raise ValueError(f"Invalid Metadata Key '{key}'")

                # validate max_drones
                if key == "max_drones":
                    if int(value) <= 0:
                        raise ValueError("max_drones must be a positive integer")

                # validate zone type
                if key == "zone":
                    if value not in ["normal", "priority", "restricted", "blocked"]:
                        raise ValueError(f"Invalid zone type '{value}'")

                # validate color
                if key == "color":
                    try:
                        hex_code = webcolors.name_to_hex(value)
                    except ValueError:
                        hex_code = None
                    value = hex_code
                metadata_dict[key] = value

        else:
            y = other

        return {
            "name": name,
            "x": int(x),
            "y": int(y),
            "color": metadata_dict["color"]
            if "color" in metadata_dict else "white",

            "zone": metadata_dict["zone"]
            if "zone" in metadata_dict else "normal",

            "max_drones": int(metadata_dict["max_drones"])
            if "max_drones" in metadata_dict else 1
        }

    def validate_config(self, config: dict) -> dict:
        try:

            parsed_config = {}
            for key, value in config.items():

                if key == "nb_drones":
                    if int(value) <= 0:
                        raise ValueError(f"{key} must be a positive_integer and greater than 0")
                    parsed_config[key] = int(value)

                elif key in ["start_hub", "end_hub"]:
                    parsed_config[key] = self.parse_hub(value)

                elif key == "hub":
                    for v in value:
                        parsed_config["hub"] = \
                            [self.parse_hub(v) for v in value]

                elif key == "connection":
                    if key not in parsed_config:
                        parsed_config[key] = []
                    for v in value:
                        connection_value = self.parse_connection(v)
                        parsed_config[key].append(connection_value)

        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(0)

        return parsed_config

    def validate_connection_hubs(self, config: dict) -> None:

        start_hub = config["start_hub"]["name"]
        end_hub = config["end_hub"]["name"]
        hubs = config.get("hub", [])
        connection = config["connection"]

        all_hubs = set()
        for hub in hubs:
            all_hubs.add(hub["name"])
        all_hubs.add(start_hub)
        all_hubs.add(end_hub)

        for c in connection:
            from_dist, to_dist = c["from"], c["to"]
            if from_dist not in all_hubs:
                raise ValueError(f"Unknown hub: {from_dist}")

            if to_dist not in all_hubs:
                raise ValueError(f"Unknown hub: {to_dist}")

    def parsing_config(self) -> dict:

        try:
            config = self.config
            mandatory_keys = [
                "nb_drones",
                "start_hub",
                "end_hub"
            ]
            extra_keys = [
                "hub",
                "connection"
            ]

            if len(sys.argv) == 2:
                filename = sys.argv[1]
                with open(filename, "r") as file:
                    first_line = True
                    for line in file:
                        line = line.strip().lower()
                        # print(line)

                        if line.startswith("#"):
                            continue

                        elif line == "":
                            continue

                        elif not line.startswith("nb_drones") and first_line is True:
                            raise ValueError("The first line must be 'nb_drones'")

                        elif ":" not in line:
                            raise ValueError("Invalid config line")

                        else:
                            key, value = line.split(":", 1)
                            key, value = key.lower().strip(), value.strip()

                            if not value:
                                raise ValueError(f"No value given for {key}")

                            if key in mandatory_keys and key in config:
                                raise ValueError(f"{key} should not be duplicated")

                            if key not in mandatory_keys and \
                                key not in extra_keys:
                                raise ValueError(f"Key: '{key}' is not Valid")
                            
                            if "#" in value:
                                value, comment = value.split("#", 1)

                            if key in mandatory_keys:
                                config[key] = value

                            elif key in extra_keys:
                                if key not in config:
                                    config[key] = []
                                config[key].append(value)
                        first_line = False

            else:
                raise ValueError("No config file given")

            if (
                "nb_drones" not in config
                or "connection" not in config
                or "start_hub" not in config
                or "end_hub" not in config
            ):
                raise ValueError("Missing a mandatory key")

            valid_config = self.validate_config(config)
            self.validate_connection_hubs(valid_config)

            # just making the (start, hub) hubs capable of holding all drones
            valid_config["start_hub"]["max_drones"] = valid_config["nb_drones"]
            valid_config["end_hub"]["max_drones"] = valid_config["nb_drones"]
            valid_config["start_hub"]["zone"] = "normal"

        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(0)

        return valid_config
