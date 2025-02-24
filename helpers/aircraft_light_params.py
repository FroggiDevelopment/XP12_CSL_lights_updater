"""
Copyright (C) 2025  Richard J.M. Muller / Froggi

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
import logging.config
from .init_logging import init_logging

# Setup logging
init_logging()
log = logging.getLogger(__name__)

AIRCRAFT_DEFINITIONS = "configs/aircrafts.json"
LIGHT_DEFINITIONS = "configs/light_params.json"


def check_if_files_are_in_correct_json_format() -> None:
    """ Checks weather the contents of the necesssary datafiles are in correct json format
    """
    try:
        with open(AIRCRAFT_DEFINITIONS, "r") as aircrafts_definitions:
            json.load(aircrafts_definitions)
    except FileNotFoundError:
        log.error("Missing aircrafts.json file. Stopping now!")
        sys.exit(1)
    except json.decoder.JSONDecodeError:
        log.error(
            "aircrafts.json may be corrupted. Please check the file for consistency!"
        )
        sys.exit(1)

    try:
        with open(LIGHT_DEFINITIONS, "r") as lights_definitions:
            json.load(lights_definitions)
    except FileNotFoundError:
        log.error("Missing light_params.json file. Stopping now!")
        sys.exit(1)
    except json.decoder.JSONDecodeError:
        log.error(
            "light_params.json might be corrupted. Please check the file for consistency!"
        )
        sys.exit(1)


def get_aircraft_categories() -> dict[str, str]:
    """returns data from the aircrafts.json file

    Returns:
        dict[str, str]: A dictionary with aircraft type and icao codes
    """
    try:
        with open(AIRCRAFT_DEFINITIONS, "r") as aircrafts_definitions:
            aircraft_categories: dict[str, str] = json.load(
                aircrafts_definitions)
    except FileNotFoundError:
        log.error("Missing aircrafts.json file. Stopping now!")
        sys.exit(1)
    except json.decoder.JSONDecodeError:
        log.error(
            "aircrafts.json may be corrupted. Please check the file for consistency!"
        )
        sys.exit(1)
    return aircraft_categories


def get_light_params_per_aircraft_category() -> dict[str, dict[str, str]]:
    """Returns data from the light_params.json file

    Returns:
        dict[str, dict[str,str]]: A dictionary with the light parameters listed per category
    """
    try:
        with open(LIGHT_DEFINITIONS, "r") as lights_definitions:
            light_params_per_category: dict[str, dict[str, str]] = json.load(
                lights_definitions)
    except FileNotFoundError:
        log.error("Missing light_params.json file. Stopping now!")
        sys.exit(1)
    except json.decoder.JSONDecodeError:
        log.error(
            "light_params.json might be corrupted. Please check the file for consistency!"
        )
        sys.exit(1)
    return light_params_per_category


def get_light_params_for_aircraft_type(aircraft_icao_type: str) -> dict[str, str]:
    """Returns the light parameters for the given aircraft type

    Args:
        aircraft_icao_type (str): Aircraft type e.g. B733 for Boeing 737-300

    Returns:
        dict[str, str]: A dictionary with the corresponding light parameters for the given aircraft type
    """
    aircrafts: dict[str, str] = get_aircraft_categories()
    light_params: dict[str, dict[str, str]
                       ] = get_light_params_per_aircraft_category()

    for key, value in aircrafts.items():
        if aircraft_icao_type in value:
            log.debug(f"{aircraft_icao_type} found in aircraft type {key}")
            return light_params[key]
    else:
        log.warning(f"{aircraft_icao_type} not found.. Using defaults!")
        return light_params["default"]
