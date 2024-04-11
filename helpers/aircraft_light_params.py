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

AIRCRAFT_DEFINITIONS = "configs/aircrafts.json"
LIGHT_DEFINITIONS = "configs/light_params.json"


def get_aircraft_categories() -> dict[str, str]:
    """Reads the aircrafts json file and returns the data

    Returns:
        dict[list]: A dictionary with the aircrafts listed per category
    """
    try:
        with open(AIRCRAFT_DEFINITIONS, "r") as aircrafts_definitions:
            aircraft_categories = json.load(aircrafts_definitions)
    except FileNotFoundError:
        logger.error("Missing aircrafts.json file. Stopping now!")
        sys.exit(1)
    except json.decoder.JSONDecodeError:
        logger.error(
            "aircrafts.json may be corrupted. Please check the file for consistency!"
        )
        sys.exit(1)
    return aircraft_categories


def get_light_params_per_aircraft_category() -> dict[str, dict[str, str]]:
    """Reads the light_params.json file and retunrs the data

    Returns:
        dict[list]: A dictionary with the light parameters listed per category
    """
    try:
        with open(LIGHT_DEFINITIONS, "r") as lights_definitions:
            light_params_per_category = json.load(lights_definitions)
    except FileNotFoundError:
        logger.error("Missing light_params.json file. Stopping now!")
        sys.exit(1)
    except json.decoder.JSONDecodeError:
        logger.error(
            "light_params.json might be corrupted. Please check the file for consistency!"
        )
        sys.exit(1)
    return light_params_per_category


def get_light_params_for_aircraft_type(aircraft_type: str) -> dict[str, str]:
    """Returns the light parameters for the given aircraft type

    Args:
        aircraft_type (str): Aircraft type e.g. B733 for Boeing 737-300

    Returns:
        dict[str]: A dictionary with the corresponding light parameters for the given aircraft type
    """
    aircrafts: dict[str, str] = get_aircraft_categories()
    light_params: dict[str, dict[str, str]] = get_light_params_per_aircraft_category()

    # Just in case that the lights are in a different object than it used to be....
    # Yeah, some CSL aircraft have multiple objetcs... don't know why

    aircraft_bodyparts = ["wings", "fuselage", "Wings", "Fuselage"]
    if (bodyparts in aircraft_type for bodyparts in aircraft_bodyparts):
        for part in aircraft_bodyparts:
            aircraft_type = aircraft_type.replace(part, "")

    for key, value in aircrafts.items():
        if aircraft_type in value:
            logger.debug(f"{aircraft_type} found in {key}")
            return light_params[key]
    else:
        logger.warning(f"{aircraft_type} not found.. Using default light params!")
        return light_params["general_aviation"]
