"""
Copyright (C) 2024  Richard J.M. Muller / Froggi

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>
"""

import sys
import json
import logging

logger = logging.getLogger("aircraft_light_params")

try:
    with open("aircrafts.json", "r") as aircrafts_definitions:
        aircrafts = json.load(aircrafts_definitions)
except FileNotFoundError:
    logger.error("Missing aircrafts.json file. Stopping now!")
    sys.exit(1)
except json.decoder.JSONDecodeError:
    logger.error(
        "aircrafts.json may be corrupted. Please check the file for consistency!"
    )
    sys.exit(1)

try:
    with open("light_params.json", "r") as lights_definitions:
        light_params = json.load(lights_definitions)
except FileNotFoundError:
    logger.error("Missing light_params.json file. Stopping now!")
    sys.exit(1)
except json.decoder.JSONDecodeError:
    logger.error(
        "light_params.json might be corrupted. Please check the file for consistency!"
    )
    sys.exit(1)


def get_light_params_for_aircraft_type(aircraft_type: str) -> dict[str]:
    """Returns the light parameters for the given aircraft type

    Args:
        aircraft_type (str): Aircraft type e.g. B733 for Boeing 737-300

    Returns:
        dict[str]: A dictionary with the corresponding light parameters for the given aircraft type
    """

    for key, value in aircrafts.items():
        if aircraft_type in value:
            logging.debug(f"{aircraft_type} found in {key}")
            return light_params[key]
    else:
        logging.warning(f"{aircraft_type} not found.. Using default light params!")
        return light_params["airliners"]


def main():

    # aircrafts_definitions = "aircrafts.json"
    # try:
    #     with open(aircrafts_definitions, "r") as fp:
    #         aircrafts = json.load(fp)
    #         print("I have aircrafts!!")
    # except FileNotFoundError:
    #     logging.info(f"File {aircrafts_definitions} not found!")

    # print(json.dumps(aircrafts))
    # with open("aircrafts.json", "w") as fp:
    #     fp.write(json.dumps(aircrafts, indent=4))

    print(json.dumps(light_params))
    with open("light_params.json", "w") as fp:
        fp.write(json.dumps(light_params, indent=4))


if __name__ == "__main__":
    main()
