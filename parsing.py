import sys
from typing import Any, List
import webcolors


class Parser:
    def __init__(self) -> None:
        self.config: dict = {}
        self.connection_hubs: list = []

    def parse_connection(self, value: str) -> dict:
        value = value.strip()

        max_link_capacity = 1
        metadata = None

        # Extract metadata
        if "[" in value or "]" in value:
            if value.count("[") != 1 or value.count("]") != 1:
                raise ValueError("Invalid metadata format for connection")

            start = value.index("[")
            end = value.index("]")

            if end < start:
                raise ValueError("Invalid metadata format for connection")

            metadata = value[start + 1:end].strip()

            # check junk after metadata
            after = value[end + 1:].strip()
            if after != "":
                raise ValueError(f"Unexpected trailing data: '{after}'")

            value = value[:start].strip()

        dist = value

        # Parse metadata
        if metadata:

            tokens = metadata.split("=")
            tokens = [t.strip() for t in tokens]
            if len(tokens) != 2 or tokens[0] != "max_link_capacity":
                raise ValueError("Invalid metadata for connection")

            key, value = tokens

            try:
                max_link_capacity = int(value)
            except ValueError:
                raise ValueError("max_link_capacity must be an integer")

            if max_link_capacity <= 0:
                raise ValueError("max_link_capacity must be positive")

        # Parse connection
        if "-" not in dist:
            raise ValueError("Invalid connection format")

        from_hub, to_hub = dist.split("-", 1)

        from_hub = from_hub.strip()
        to_hub = to_hub.strip()

        if not from_hub or not to_hub:
            raise ValueError("Invalid connection format")

        connection = {from_hub, to_hub}

        if connection in self.connection_hubs:
            raise ValueError("Duplicate connection")

        self.connection_hubs.append(connection)

        return {
            "from": from_hub,
            "to": to_hub,
            "max_link_capacity": max_link_capacity,
        }

    def tokenize_metadata(self, tokens: List) -> List[str]:
        pairs = []

        i = 0
        while i < len(tokens):

            if "=" in tokens[i]:
                pairs.append(tokens[i])
                i += 1

            elif (
                i + 2 < len(tokens)
                and tokens[i + 1] == "="
            ):
                pairs.append(
                    f"{tokens[i]}={tokens[i + 2]}"
                )
                i += 3

            else:
                raise ValueError(
                    f"Invalid metadata near '{tokens[i]}'"
                )

        return pairs

    def parse_hub(self, value: str) -> dict:
        value = value.strip()
        metadata_dict: dict = {}
        metadata = None

        if "[" in value or "]" in value:
            if value.count("[") != 1 or value.count("]") != 1:
                raise ValueError("Invalid format")

            start = value.index("[")
            end = value.index("]")

            if end < start:
                raise ValueError("Invalid metadata format")

            metadata = value[start + 1:end].strip()

            # check junk after metadata
            after = value[end + 1:].strip()
            if after != "":
                raise ValueError(f"Unexpected trailing data: '{after}'")

            value = value[:start].strip()

        # Parse: name x y
        parts = value.split()

        if len(parts) != 3:
            raise ValueError("Hub must contain exactly: name x y")

        name, x_str, y_str = parts

        # Validate name
        if "-" in name:
            raise ValueError(f"Invalid zone name '{name}'")

        # Validate coordinates
        try:
            x = int(x_str)
            y = int(y_str)
        except ValueError:
            raise ValueError("Coordinates must be integers")

        # Parse metadata
        if metadata:

            tokens = metadata.split()
            metadata_pairs = self.tokenize_metadata(tokens)

            for pair in metadata_pairs:
                if "=" not in pair:
                    raise ValueError(f"Invalid metadata '{pair}'")

                key, value = pair.split("=", 1)

                if key not in ("zone", "color", "max_drones"):
                    raise ValueError(f"Invalid metadata key '{key}'")

                # validate max_drones
                if key == "max_drones":
                    try:
                        max_drones = int(value)
                    except ValueError:
                        raise ValueError("max_drones must be an integer")

                    if max_drones <= 0:
                        raise ValueError("max_drones must be positive")

                    if key in metadata_dict:
                        raise ValueError(f"Duplicate metadata key '{key}'")

                    metadata_dict[key] = max_drones

                # validate zone
                if key == "zone":
                    if value not in ["normal",
                                     "priority",
                                     "restricted",
                                     "blocked"]:
                        raise ValueError(f"Invalid zone type '{value}'")

                    if key in metadata_dict:
                        raise ValueError(f"Duplicate metadata key '{key}'")

                    metadata_dict[key] = value

                # validate color
                if key == "color":
                    try:
                        hex_code = webcolors.name_to_hex(value)
                    except ValueError:
                        hex_code = None
                    value = hex_code

                    if key in metadata_dict:
                        raise ValueError(f"Duplicate metadata key '{key}'")

                    metadata_dict[key] = value

        return {
            "name": name,
            "x": x,
            "y": y,
            "color": metadata_dict.get("color", "white"),
            "zone": metadata_dict.get("zone", "normal"),
            "max_drones": metadata_dict.get("max_drones", 1),
        }

    def validate_config(self, config: dict) -> dict:
        try:
            parsed_config: dict[str, Any] = {}
            for key, value in config.items():
                if key == "nb_drones":
                    if int(value) <= 0:
                        raise ValueError(
                            f"{key} must be a positive_integer "
                            "and greater than 0"
                        )
                    parsed_config[key] = int(value)

                elif key in ["start_hub", "end_hub"]:
                    parsed_config[key] = self.parse_hub(value)

                elif key == "hub":
                    for v in value:
                        parsed_config["hub"] = [
                            self.parse_hub(v)
                            for v in value
                        ]

                elif key == "connection":
                    if key not in parsed_config:
                        parsed_config[key] = []
                    for v in value:
                        connection_value = self.parse_connection(v)
                        parsed_config[key].append(connection_value)

                elif key == "no_render":
                    parsed_config[key] = bool(value)

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
            mandatory_keys = ["nb_drones", "start_hub", "end_hub"]
            extra_keys = ["hub", "connection"]

            filename = None
            no_render = False

            for arg in sys.argv[1:]:
                if arg == "--no-render":
                    no_render = True
                elif not arg.startswith("--"):
                    filename = arg

            if filename is None:
                raise ValueError("No config file given")

            config["no_render"] = no_render

            with open(filename, "r") as file:
                first_line = True
                for line in file:
                    line = line.strip().lower()

                    # line starts with comment #
                    if line.startswith("#"):
                        continue

                    # empty line
                    elif line == "":
                        continue

                    # if nb_drones is not the first line
                    elif (
                            not line.startswith("nb_drones")
                            and first_line is True
                    ):
                        raise ValueError("The first line must "
                                         "be 'nb_drones'")

                    # if there is no colon in the line
                    elif ":" not in line:
                        raise ValueError("Invalid config line")

                    else:
                        key, value = line.split(":", 1)
                        key, value = key.strip(), value.strip()

                        # if there is no value
                        if not value:
                            raise ValueError(f"No value given for {key}")

                        # if key is duplicated
                        if key in mandatory_keys and key in config:
                            raise ValueError(f"{key} should not be duplicated")

                        # if key is not a mandatory or extra key
                        if key not in mandatory_keys and key not in extra_keys:
                            raise ValueError(f"Key: '{key}' is not Valid")

                        # if key has a comment
                        if "#" in value:
                            value, comment = value.split("#", 1)

                        # if key is a mandatory key
                        if key in mandatory_keys:
                            config[key] = value

                        # if key is an extra key
                        elif key in extra_keys:
                            if key not in config:
                                config[key] = []
                            config[key].append(value)
                    first_line = False

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

        # print(valid_config)
        return valid_config
