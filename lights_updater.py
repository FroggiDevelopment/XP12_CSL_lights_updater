#!/usr/bin/env python3
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
import re
import argparse
import logging
from pathlib import Path
from configparser import ConfigParser, NoSectionError, NoOptionError
from typing import Callable

from helpers import make_backup
from helpers import remove_backups
from helpers import recover_from_backup
from helpers import remove_xpmp2_files
from helpers import copy_new_to_old
from helpers import get_light_params_for_aircraft_type
from helpers import get_aircraft_objects_from_xsb_file
from helpers import get_aircraft_categories
from helpers import get_list_of_animations
from helpers import check_if_files_are_in_correct_json
from helpers import get_description
from helpers import init_logging
from helpers import paused_exit

from light_converters import convert_airplane_landing_lights
from light_converters import convert_airplane_taxi_lights
from light_converters import convert_airplane_nav_lights
from helpers import convert_airplane_beacon_lights
from helpers import convert_airplane_flashing_beacon_lights
from helpers import convert_airplane_strobe_lights
from helpers import convert_airbus_strobe_lights

from helpers.custom_exceptions import NoAnimationFoundError
from helpers.custom_exceptions import WrongLightInAnimationError

from decorators.time_benchmark import named_time_benchmark, time_benchmark
from configs._version import __version__

# Setup logging
init_logging()
log = logging.getLogger("lights_updater")

# Some constants
TEMP_FILE_SUFFIX: str = ".TEMP"

OLD_AIRCRAFT_LIGHTS: dict[str, str] = {
    "airplane_landing": "airplane_landing",
    "airplane_landing_core": "airplane_landing",
    "airplane_landing_glow": "airplane_landing",
    "airplane_landing_flare": "airplane_landing",
    "airplane_landing_sp": "airplane_landing",
    "airplane_taxi": "airplane_taxi",
    "airplane_taxi_core": "airplane_taxi",
    "airplane_taxi_flare": "airplane_taxi",
    "airplane_taxi_glow": "airplane_taxi",
    "airplane_taxi_sp": "airplane_taxi",
    "airplane_nav": "airplane_nav",
    "airplane_nav_sp": "airplane_nav",
    "airplane_nav_left": "airplane_nav",
    "airplane_nav_sp_left": "airplane_nav",
    "airplane_nav_right": "airplane_nav",
    "airplane_nav_sp_right": "airplane_nav",
    "airplane_nav_tail": "airplane_nav",
    "airplane_nav_tail_size": "airplane_nav",
    "airplane_nav_left_size": "airplane_nav",
    "airplane_nav_right_size": "airplane_nav",
    "airplane_strobe": "airplane_strobe",
    "airplane_strobe_sp": "airplane_strobe",
    "airplane_strobe_left": "airplane_strobe",
    "airplane_strobe_right": "airplane_strobe",
    "airplane_strobe_tail": "airplane_strobe",
    "airplane_strobe_omni": "airplane_strobe",
    "airplane_strobe_dir": "airplane_strobe",
    "airplane_beacon": "airplane_beacon",
    "airplane_beacon_sp": "airplane_beacon",
    "airplane_beacon_rotate": "airplane_beacon",
    "airplane_beacon_rotate_sp ": "airplane_beacon",
    "airplane_beacon_strobe": "airplane_beacon",
    "airplane_beacon_strobe_sp": "airplane_beacon",
}

POSITION_IDENTIFIERS: dict[str, str] = {
    "_left": "",
    "_right": "",
    "_tail": ""
}

flashing_beacons: bool = False


def remove_positional_name_from_line(line: str) -> str:
    """Removes added or existing positional identifiers from line

    Args:
        line (str): line with positional identifiers

    Returns:
        str: line without positional identifiers
    """
    if any((unwanted_position_information := position) in line for position in POSITION_IDENTIFIERS):
        line = line.replace(unwanted_position_information,
                            POSITION_IDENTIFIERS[unwanted_position_information])
    return line


def split_object_file(object_file: str) -> tuple[str, str]:
    """Splits the object file in object part and animation part

    Args:
        object_file (str): object containing all ariplane data

    Returns:
        tuple[str, str]: split airplane object with [1] containing the object definitions
                         and [1] the animations, i.e. lights etc.
    """
    split_pattern = r"(?=ANIM_begin)"
    object_parts = re.split(split_pattern, object_file, maxsplit=1)
    if len(object_parts) == 2:
        object_definitions = object_parts[0]
        animations = object_parts[1]

        return object_definitions, animations
    raise NoAnimationFoundError


def process_animations_section(animations: str, aircraft_icao_type: str) -> str:
    """ Process the animations section where light parameters are defined

    Args:
        animations (str): Text content with animations and light parameters
        aircraft_icao_type (str): ICAO type of aircraft for getting the light parameters

    Returns:
        str: Processed text content with light parameters converted to XP 12 standard
    """
    _lighttype_per_dataref: dict[str, str] = {
        "libxplanemp/controls/landing_lites_on": "airplane_landing",
        "libxplanemp/controls/taxi_lites_on": "airplane_taxi",
        "libxplanemp/controls/nav_lites_on": "airplane_nav",
        "libxplanemp/controls/beacon_lites_on": "airplane_beacon",
        "libxplanemp/controls/strobe_lites_on": "airplane_strobe",
    }

    _light_converters: dict[str, Callable[[str, dict[str, str]], str]] = {
        "airplane_landing": convert_airplane_landing_lights,
        "airplane_taxi": convert_airplane_taxi_lights,
        "airplane_nav": convert_airplane_nav_lights,
        "airplane_beacon": convert_airplane_beacon_lights,
        "airplane_beacon_flashing": convert_airplane_flashing_beacon_lights,
        "airplane_airbus_strobe": convert_airbus_strobe_lights,
        "airplane_strobe": convert_airplane_strobe_lights
    }

    # TODO: Move this list to a config or at least up in this code
    # To get the typical Airbus strobe flash sequence the strobes must be converted differently
    airbus_icaos: list[str] = [
        "A19N",
        "A20N",
        "A21N",
        "A306",
        "A30B",
        "A310",
        "A318",
        "A319",
        "A320",
        "A321",
        "A332",
        "A333",
        "A337",
        "A338",
        "A339",
        "A342",
        "A343",
        "A345",
        "A346",
        "A359",
        "A35K",
        "A388",
        "A3ST",
        "BCS1",
        "BCS3"
    ]

    light_params_dict: dict[str, dict[str, str]] = get_light_params_for_aircraft_type(
        str(aircraft_icao_type)
    )

    list_of_animations: list[str] = get_list_of_animations(animations)

    for animation in list_of_animations:
        _animation = animation.replace("LIGHT_NAMED", "LIGHT_PARAM")

        if any((light_dataref := dataref) in animation for dataref in _lighttype_per_dataref.keys()):
            light_type: str = _lighttype_per_dataref[light_dataref]
            light_converter = _light_converters[light_type]

            if light_dataref == "libxplanemp/controls/beacon_lites_on" and flashing_beacons is True:
                aircraft_categories = get_aircraft_categories()
                for category in aircraft_categories.items():
                    if aircraft_icao_type in category[1] and category[0] in ["medium", "high"]:
                        light_converter = _light_converters["airplane_beacon_flashing"]

            if light_dataref == "libxplanemp/controls/strobe_lites_on" and aircraft_icao_type in airbus_icaos:
                light_converter = _light_converters["airplane_airbus_strobe"]

            try:
                new_animation: str = light_converter(
                    _animation, light_params_dict[light_type])
            except WrongLightInAnimationError as err:
                log.error(err)
                continue

            animations = animations.replace(animation, new_animation)

    return animations


@time_benchmark
def process_object_files(aircraft_objects: list[dict[str, str]]) -> None:
    """Create new aircraft obj file with X-Plane 12 light params
    Args:
        aircraft_objects: A list with dictionaries containing icao_type of
                          aircraft and path to the object file.
    """
    for aircraft_object in aircraft_objects:
        aircraft_object_path: Path = Path(aircraft_object["full_object_path"])

        aircraft_object_content: str = ""
        try:
            with open(aircraft_object_path, "r", errors="replace") as file:
                aircraft_object_content = file.read()
        except FileNotFoundError:
            log.error(f"{aircraft_object['full_object_path']} not found!")
            continue
        except UnicodeDecodeError as err:
            log.error(
                f"Object file seems damaged! See: {err}\n Trying to repair it.")
            continue

        if aircraft_object_content == "":
            continue
        try:
            object_definitions, animations = split_object_file(
                aircraft_object_content)
        except NoAnimationFoundError:
            log.debug(f"No animations found in {aircraft_object_path}!")
            continue

        log.info(f"Processing {aircraft_object_path}")
        new_animations_section = process_animations_section(
            animations, aircraft_object["icao_type"])

        # Glue the two file parts together
        new_file_content = object_definitions + new_animations_section

        # Write converted data to temp-file
        temp_object_file: Path = Path(aircraft_object_path).with_suffix(
            suffix=TEMP_FILE_SUFFIX
        )
        try:
            with open(temp_object_file, "w+") as new_obj_file:
                new_obj_file.write(new_file_content)
        except IOError as err:
            log.error("Something went wrong!", err)


def set_csl_path() -> str:
    """Set a minimal configuration.

    Args:
        args_path_to_csl (str | None): If available the path is set by commandline param.

    Returns:
        Path: Returns path to CSL files
    """
    config = ConfigParser()
    config.read("configs/config.ini")

    if config.read("configs/config.ini") != []:
        try:
            return config.get("csl", "csl_path").strip('"')
        except NoSectionError:
            log.error(
                "No csl section found in config.ini! Please check your config file!")
            paused_exit()
        except NoOptionError:
            log.error(
                "No csl_path option found in config.ini! Please check your config file!")
            paused_exit()
    return ""


def parse_args() -> argparse.Namespace:
    """Parses commandline arguments

    Returns:
        argparse.Namespace: argparser arguments
    """
    DESCRIPTION, EPILOG = get_description()
    # Check if cli params are present
    parser = argparse.ArgumentParser(
        prog="Lights updater for CSL objects",
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-p",
        "--path",
        required=False,
        type=Path,
        default=None,
        action="store",
        metavar="path",
        dest="csl_path",
        help="Set path to location of CSL aircrafts.\n"
        "If there are whitespaces in the path,\nyou MUST use quotation marks around the path!\n"
        "To be save: Always use them.",
    )

    parser.add_argument(
        "-f",
        "--flashing-beacons",
        required=False,
        action="store_true",
        help="Sets the beacons to be flashing beacons on bigger airplanes!",
    )

    parser.add_argument(
        "-u",
        "--undo",
        required=False,
        action="store_true",
        help="Rolls back the previous made changes!",
    )

    parser.add_argument(
        "-r",
        "--remove-backups",
        action="store_true",
        help="Removes the backup files. Be careful!",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s version: {__version__}",
    )
    parser._optionals.title = "Optional arguments"

    return parser.parse_args()


@named_time_benchmark("lights_updater")
def main(args: argparse.Namespace, csl_path: Path) -> None:
    """Here all the magic happens.

    Args:
        args (argparse.Namespace): commandline arguments See -h for help
        csl_path (str): The startpath for searching the xsb_aircraft.txt files
    """
    # Check if aircrafts.json and light_params.json exist and are correct. If not stop!
    if not check_if_files_are_in_correct_json():
        paused_exit()

    # Get the list of aircraft objects and its file locations
    aircraft_objects: list[dict[str, str]] = get_aircraft_objects_from_xsb_file(
        searchpath=csl_path)

    # Special actions first!

    if args.undo:  # Undo changes, recover object from backup.
        recover_from_backup(aircraft_objects)
        return

    if args.remove_backups:  # Remove the backupfiles.
        remove_backups(aircraft_objects)
        return

    # Start of main processing
    log.info("Creating backups!")
    make_backup(aircraft_objects=aircraft_objects)

    log.info(
        "Removing possible xpmp2 files as they can 'cache' the objects.")
    log.info("They should be recreated on the fly while you use X-Plane."
             )
    remove_xpmp2_files(filepath=csl_path)

    log.info(
        "Start processing! Duration depends on number of files and of course general hardware performance."
    )
    process_object_files(aircraft_objects)

    copy_new_to_old(aircraft_objects, TEMP_FILE_SUFFIX)

    log.info(
        f"Processing done, {len(aircraft_objects)} files have been processed!")


if __name__ == "__main__":
    args = parse_args()
    # To set this var as global, I do it here. Rest is set in the main() function
    if args.flashing_beacons:
        flashing_beacons = True
        log.debug(f"Using flashing beacons: {flashing_beacons}")

    if args.csl_path is not None:
        csl_path = args.csl_path
    else:
        csl_path = set_csl_path()

    csl_path = Path(csl_path)
    if csl_path.is_dir() is False:
        log.info(
            "CSL path seems not to be a valid directory! Please check the path!")
        paused_exit()
    main(args, csl_path)
    paused_exit()
