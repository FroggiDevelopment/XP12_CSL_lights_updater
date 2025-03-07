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
import sys
import argparse
import logging
import logging.config
from pathlib import Path
from configparser import ConfigParser

from helpers import make_backup
from helpers import remove_backups
from helpers import recover_from_backup
from helpers import remove_xpmp2_files
from helpers import copy_new_to_old
from helpers import get_light_params_for_aircraft_type
from helpers import get_aircraft_objects_from_xsb_file
from helpers import fix_lights_anomalies
from helpers import filter_unwanted_light_params
from helpers import add_lateral_position_to_lights
from helpers import check_if_files_are_in_correct_json_format
from helpers import get_description
from helpers import init_logging
from decorators.time_benchmark import named_time_benchmark, time_benchmark
from configs._version import __version__

# Setup logging
init_logging()
log = logging.getLogger("lights_updater")

# Some constants
TEMP_FILE_SUFFIX: str = ".TEMP"
STOP_ON_ERROR: bool = True
LIGHT_NEEDLES: list[str] = [
    "airplane_landing",
    "airplane_taxi",
    "airplane_nav",
    "airplane_nav_left",
    "airplane_nav_right",
    "airplane_nav_tail",
    "airplane_strobe",
    "airplane_beacon",
    "airplane_beacon_rotate",
    "airplane_beacon_strobe",
]

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


def remove_positional_name_from_line(line: str) -> str:
    """Removes added or existing positional identifiers from line

    Args:
        line (str): line with positional identifiers

    Returns:
        str: line without positional identifiers
    """
    if any((unwanted_position_information := position) in line for position in POSITION_IDENTIFIERS):
        log.debug(f"Found {unwanted_position_information} in line {line}!")
        line = line.replace(unwanted_position_information,
                            POSITION_IDENTIFIERS[unwanted_position_information])
    return line


def reduce_spill_intensity(line: str) -> str:
    """Reduces the groundspill intensity of a light

    Args:
        line (str): A string with light specific parameters

    Returns:
        str: A line with reduced intensity
    """
    reduce_factors = {
        "airplane_nav": 0.50,
        "airplane_beacon": 0.50,
        "airplane_strobe": 0.75
    }

    split_line = line.split()
    intensity = int(split_line[9].replace("cd", ""))

    reduced_intensity = int(intensity * reduce_factors[split_line[1]])
    split_line[9] = f"{str(reduced_intensity)}cd"
    line_to_return = " ".join(split_line)

    return line_to_return


def process_lights(line: str, light_params: dict[str, str]) -> str:
    """Changes the light parameters to XP12 specs

    Args:
        line (str): A string with light specifics parameters
        light_params (dict[str, str]): A dictionary with the light parameters

    Returns:
        str: A line with updated light parameters
    """
    # Remove possible unwanted params
    # Keep specifier, lighttype, x, y, z params
    line = " ".join(line.split()[:5])

    # Remove billboard lines, will be (re)build later on.
    if "_bb" in line:
        return ""

    # Remove pm suffix
    line = line.replace("_pm", "")

    if "airplane_nav" in line or "airplane_strobe" in line:
        line = add_lateral_position_to_lights(line)

    lighttype = line.split()[1]

    line = line.replace("\n", "")
    line += f" {light_params[lighttype]}\n"

    if any(position in line for position in POSITION_IDENTIFIERS.keys()):
        line = remove_positional_name_from_line(line)

    lighttype = line.split()[1]

    # TODO: Treat _pm (groundspill) different then the _bb (billboard)
    if any([light in line for light in ["airplane_nav", "airplane_beacon", "airplane_strobe"]]):
        reduced_intensity_line = reduce_spill_intensity(line)
        reduced_intensity_line = reduced_intensity_line.replace(
            f"{lighttype}", f"{lighttype}_pm")
        line = line.replace(
            f"{lighttype}", f"{lighttype}_bb") + reduced_intensity_line
        line = f"{line}\n"
    else:
        line = line.replace(f"{lighttype}", f"{lighttype}_pm")
        line += line.replace("_pm", "_bb")

    return line


@time_benchmark
def process_object_files(aircraft_objects: list[dict[str, Path]]) -> None:
    """Create new aircraft obj file with X-Plane 12 light params
    Args:
        aircraft_objects: A list with dictionaries containing icao_type of
                          aircraft and path to the object file.
    """
    for aircraft_object in aircraft_objects:

        light_params: dict[str, str] = get_light_params_for_aircraft_type(
            str(aircraft_object["icao_type"])
        )
        aircraft_object_path: Path = Path(aircraft_object["full_object_path"])

        aircraft_object_content: list[str] = []
        try:
            with open(aircraft_object_path, "r", errors="replace") as file:
                aircraft_object_content = file.readlines()
        except FileNotFoundError:
            log.error(f"{aircraft_object['full_object_path']} not found!")
            continue
        except UnicodeDecodeError as err:
            log.error(
                f"Object file seems damaged! See: {err}\n Trying to repair it.")
            continue

        temp_object_file: Path = Path(aircraft_object_path).with_suffix(
            suffix=TEMP_FILE_SUFFIX
        )

        if aircraft_object_content == []:
            continue
        new_file_content = ""
        log.info(f"Processing {aircraft_object_path}")

        known_light_coordinates: list[str] = []

        for line in aircraft_object_content:
            # First filter the lights
            line = filter_unwanted_light_params(line)

            # Ignore comment lines.
            if line.strip().startswith("#"):
                continue

            # Handle rotating beacons and avoid duplicates
            coordinates = f"{':'.join(line.split()[2:5])}"

            # Replace all 'odd' light params with the XP12 supported ones according to available information.
            # Things like _sp, _size, _core, _glow, etc.
            if any((old_light_param := lighttype) in line.split() for lighttype in OLD_AIRCRAFT_LIGHTS):
                if coordinates in known_light_coordinates:
                    log.debug(
                        f"{old_light_param} at {coordinates} already processed for ICAO {aircraft_object['icao_type']}")
                    line = ""
                    continue
                else:
                    known_light_coordinates.append(coordinates)
                    line = line.replace(
                        old_light_param, OLD_AIRCRAFT_LIGHTS[old_light_param])

            if any(lighttype in line for lighttype in LIGHT_NEEDLES):
                line = process_lights(line, light_params)

            new_file_content += line

        # Fix possible error in the taxilight dataref
        new_file_content = fix_lights_anomalies(new_file_content)

        # Write converted data to temp-file
        try:
            with open(temp_object_file, "w+") as new_obj_file:
                new_obj_file.write(new_file_content)
        except IOError as err:
            log.error("Something went wrong!", err)


def set_config(args_path_to_csl: str | None) -> tuple[str, bool]:
    """Set a minimal configurationq.

    Args:
        args_path_to_csl (str | None): If available the path is set by commandline param.

    Returns:
        tuple[str, bool]: Returns a path-string and a bool for STOP_ON_ERROR
    """
    # Get config from file

    config = ConfigParser()

    if config.read("configs/config.ini") != []:
        pass
    else:
        log.error("No config file found!")
        sys.exit()

    if '"' in config["csl"]["csl_path"]:
        config["csl"]["csl_path"] = config["csl"]["csl_path"].strip('"')
    if config["csl"]["csl_path"] == "" and args_path_to_csl is None:
        log.error(
            "No CSL path specified! Please update configs/config.ini or specify it by using -p or --path!"
        )
        sys.exit()

    STOP_ON_ERROR = config.getboolean("generic", "STOP_ON_ERROR")

    if args_path_to_csl is not None:
        return args_path_to_csl, STOP_ON_ERROR
    else:
        return config["csl"]["csl_path"], STOP_ON_ERROR


def parse_args() -> argparse.Namespace:
    """Parse commandline arguments.

    Returns:
        tuple[str, bool]: Returns a path-string and a bool for STOP_ON_ERROR
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


def paused_exit():
    input("Press any key to continue...")
    sys.exit()


@named_time_benchmark("lights_updater")
def main(args: argparse.Namespace, CSL_PATH: str, STOP_ON_ERROR: bool) -> None:
    """Here all the magic happens.

    Args:
        args (argparse.Namespace): commandline arguments See -h for help
        CSL_PATH (str): The startpath for searching the xsb_aircraft.txt files
        STOP_ON_ERROR (bool): A boolean to determine the behavior on errors.
    """
    # Check if aircrafts.json and light_params.json exist and are correct. If not stop!
    check_if_files_are_in_correct_json_format()

    # Get the list of aircraft objects and its file locations
    aircraft_objects: list[dict[str, str]] = get_aircraft_objects_from_xsb_file(
        searchpath=CSL_PATH)

    # Special actions first!
    if args.undo:  # Undo changes, recover object from backup.
        recover_from_backup(aircraft_objects, STOP_ON_ERROR)
        return

    if args.remove_backups:  # Remove the backupfiles.
        remove_backups(aircraft_objects)
        return

    # Start of main processing
    log.info("Creating backups!")
    make_backup(aircraft_objects=aircraft_objects, stop_on_error=STOP_ON_ERROR)

    log.info(
        "Removing possible xpmp2 files as they can 'cache' the objects. \
        They should be recreated on the fly while you use X-Plane."
    )
    remove_xpmp2_files(filepath=CSL_PATH)

    log.info(
        "Start processing! Duration depends on number of files and of course general hardware performance."
    )
    process_object_files(aircraft_objects)

    copy_new_to_old(aircraft_objects, TEMP_FILE_SUFFIX)

    log.info(
        f"Processing done, {len(aircraft_objects)} files have been processed!")


if __name__ == "__main__":
    args = parse_args()
    csl_path, stop_on_error = set_config(args.csl_path)
    main(args, csl_path, stop_on_error)
    paused_exit()
