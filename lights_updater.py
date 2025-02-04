#!/usr/bin/env python3.10
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
import argparse
import logging
import logging.config
import json
from pathlib import Path
from configparser import ConfigParser

from helpers import make_backup
from helpers import delete_files
from helpers import recover_from_backup
from helpers import remove_xpmp2_files
from helpers import get_light_params_for_aircraft_type
from helpers import get_aircraft_objects_from_xsb_file
from helpers import fix_lights_anomalies
from helpers import check_if_files_are_in_correct_json_format
from decorators.time_benchmark import named_time_benchmark, time_benchmark
from configs._version import __version__

# Setup logging
with open('configs/logging.conf', 'r') as configfile:
    try:
        logger_config = json.load(configfile)
    except FileNotFoundError:
        ("Missing logging.conf file. Stopping now!")
        sys.exit(1)
    except json.decoder.JSONDecodeError:
        print(
            "Logging config might be corrupted. Please check the configfile for consistency!"
        )
        sys.exit(1)
    
logging.config.dictConfig(logger_config)

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
LIGHTS_TO_IGNORE = [
    "headlight",
    "_size",
    "_sp",
    "taillight",
    "_core",
    "_size",
    "_omni",
    "_dir",
    "airplane_strobe_omni",
    "airplane_beacon_",
    "full_custom_halo_night",
    "_glow",
    "_flare",
    "logo",
    "PLN_",
    "_core",
    "_flare",
    "_glow",
    "LIGHT_SPILL_CUSTOM",
]

POSITION_IDENTIFIERS = ["_left", "_right", "_tail"]

def filter_unwanted_light_params(line: str) -> str:
    """Filter out light params that are old or otherwise wrong.
       Can be expanded for future cases.

    Args:
        line (str): Line with light parameters

    Returns:
        str: Corrected line with light parameters
    """
    
    # If light is on the ignore list, ignore it and retrun empty line
    if any(to_ignore in line for to_ignore in LIGHTS_TO_IGNORE):
        return ""
    
    # Check if old LIGHT_NAMED param exists and replace it with the new one
    if "LIGHT_NAMED" in line:
        log.debug(f"Replacing LIGHT_NAMED in line {line} to LIGHT_PARAM")
        line = line.replace("LIGHT_NAMED", "LIGHT_PARAM")
    
    # Some lines are commented out... Must be undone
    if "#LIGHT_PARAM" in line or "#LIGHT_NAMED" in line:
        log.debug(f"Removing leading # from line {line}")
        line = line.replace("#LIGHT_PARAM", "LIGHT_PARAM")      

    # Remove positional name from line
    if any(position in line for position in POSITION_IDENTIFIERS):
        for item in POSITION_IDENTIFIERS:
            line = line.replace(item, "")

    return line

def add_lateral_position_to_lights(line: str) -> str:
    """To determine directional parameters add left, right or tail to the light param
       based on x-y-position of the light.
       Will be removed again later on in the process.

    Args:
        line (str): Line with light-parameters.

    Returns:
        str: Line with 'positional' light-name-parameters. I.e. airplane_nav_rigt
    """
    # If the line already includes position, return it unprocessed.
    if any(position in line for position in POSITION_IDENTIFIERS):
        return line

    _x_position = float(line.split()[2:3][0])
    actual_lighttype = line.split()[1]

    if (_x_position) > -0.50 and _x_position < 0.50:
        lighttype = f"{actual_lighttype}_tail"
    elif (_x_position) < -0.50:
        lighttype = f"{actual_lighttype}_left"
    else:
        lighttype = f"{actual_lighttype}_right"

    return line.replace(actual_lighttype, lighttype)

def remove_positional_name_from_line(line: str) -> str:
    """Removes added or existing positional identifiers from line

    Args:
        line (str): line with positional identiefers

    Returns:
        str: line without positional identifiers
    """
    line = line.replace("_right", "")
    line = line.replace("_left", "")
    line = line.replace("_tail", "")
    return line

def process_lights(line: str, light_params: dict[str, str]) -> str:
    """Changes the light parameters to XP12 specs

    Args:
        line (str): A string with light specifics parameters
        light_params (dict[str, str]): A dictionary with the light parameters

    Returns:
        str: A line with updated light parameters
    """
    
    # Remove possible unwanted params, keep specifier, lighttype, x, y, z params
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

    line = line.replace(f"{lighttype}", f"{lighttype}_pm")
    line += line.replace("_pm", "_bb")
    
    if any(position in line for position in POSITION_IDENTIFIERS):
        line = remove_positional_name_from_line(line)
        
    return line


@time_benchmark
def process_object_files(aircraft_objects: list[dict[str, Path]]) -> None:
    """Create new aircraft obj file with X-Plane 12 light params
    TODO: Correct the nonsense below... file is not an argument to this function
    Args:
        file (Path): the existing aircraft object file
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
        except FileNotFoundError as err:
            log.error(f"{aircraft_object['full_object_path']} not found!")
            continue
        except UnicodeDecodeError as err:
            log.error(f"Object file seems damaged! See: {err}\n Trying to repair it.")
            continue

        temp_object_file: Path = Path(aircraft_object_path).with_suffix(
            suffix=TEMP_FILE_SUFFIX
        )

        if aircraft_object_content == []:
            continue
        new_file_content = ""
        log.info(f"Processing {aircraft_object_path}")
        for line in aircraft_object_content:
            # First filter the lights
            line = filter_unwanted_light_params(line)
            
            # Remove some unnecessary lines. Can be done better...!!!
            if line.startswith("# "):
                continue

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


def copy_new_to_old(aircraft_objects: list[dict[str,str]])-> None:
    """Copy the new created file over the original file
    Delete the new file
    """
    log.info("Start copying processed files to original file!")
    for aircraft_object in aircraft_objects:
        destination_file = Path(aircraft_object["full_object_path"]).with_suffix(".obj")
        temp_object_file = Path(aircraft_object["full_object_path"]).with_suffix(TEMP_FILE_SUFFIX)

        try:
            destination_file.write_bytes(temp_object_file.read_bytes())
        except PermissionError as err:
            if STOP_ON_ERROR is True:
                log.error("Stopping on error!", err)
                sys.exit()
            else:
                continue
        except FileNotFoundError as err:
            log.error(f"File could not be copied! See: {err}")
            continue
        try:
            temp_object_file.unlink()
        except PermissionError as err:
            log.error(f"{temp_object_file.name} can not be deleted!", err)
            if STOP_ON_ERROR is True:
                sys.exit()
        log.info(f"Copying {temp_object_file.name} to {aircraft_object['full_object_path']} file done.")


def set_config(args_path_to_csl: str | None) -> tuple[str, bool]:
    """Set a minimal configuration settings.

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

    if config["csl"]["csl_path"] == "" and args_path_to_csl == None:
        log.error(
            "No CSL path specified! Please update configs/config.ini or specify it by using -p or --path!"
        )
        sys.exit()

    STOP_ON_ERROR = config.getboolean("generic", "STOP_ON_ERROR")

    if args_path_to_csl != None:
        return args_path_to_csl, STOP_ON_ERROR
    else:
        return config["csl"]["csl_path"], STOP_ON_ERROR


def parse_args() -> argparse.Namespace:
    """Parse commandline arguments.

    Returns:
        tuple[str, bool]: Returns a path-string and a bool for STOP_ON_ERROR
    """
    # Check if cli params are present
    parser = argparse.ArgumentParser(
        prog="Lights updater for CSL objects",
        description="""This program can convert XP11 lightparams of CSL aircraft objects to the new XP12 specifications.
Developed for getting landing lights for LifeTraffic.
Works with Bluebell and X-CSL packages, works only with some custom CSL aircraft.

For normal start you don't need any arguments.
But then you \x1b[1;4;31mMUST\x1b[0m specify the csl_path in the config.ini file!""",
        epilog="""
\x1b[1;31mAttention!!
If you specify a path with -p / --path when processing the objects and you want to undo your changes,
or remove the backup files with -r / --remove-backups, you need the specify the path again!
If you don't and there is a path specified in the config.ini, results may not be what you expected!\x1b[0m

Now you know!\n
""",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-p",
        "--path",
        required=False,
        type=Path,
        default=None,
        action="store",
        metavar="csl_path",
        dest="csl_path",
        help="Set path to location of CSL aircrafts.\n"
        "Be aware that if there are whitespaces in the path, you MUST use quotation marks around the CSL_PATH!\nTo be save, always use them.",
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

@time_benchmark
def remove_backups(aircraft_objects: list[dict[str, str]]) -> None:
    """Removes previous backups. This is not reversible!

    Args:
        aircraft_objects (list[dict[str, str]]): A list with all aircraft objects
                                                 including path information
    """
    files_to_remove: list[Path] = []
    log.info("\x1b[1;31mBackups will be removed now! This is permanent!\x1b[0m")
    yes_no = input("Are you sure? \x1b[1;31myes\x1b[0m/\x1b[1;32mNo\x1b[0m]" or "No")
    if yes_no.lower() == "yes" or yes_no.lower() == "y":
        log.info("Okay! Let's do it....!!")
        for aircraft_object in aircraft_objects:
            files_to_remove.append(Path(aircraft_object["full_object_path"]))      
        delete_files(files_to_remove, ".BCK")
        log.info("Backup files removed successfully!")
    sys.exit()

@named_time_benchmark("lights_updater")
def main(args: argparse.Namespace, CSL_PATH: str, STOP_ON_ERROR: bool) -> None:
    """Here all the magic happens.

    Args:
        args (argparse.Namespace): coammndline arguments See -h for help
        CSL_PATH (str): The startpath for searching the xsb_aircraft.txt files
        STOP_ON_ERROR (bool): A boolean to determine the behevior on errors.
    """
    # Check if aircrafts.json and light_params.json exist and are correct. If not stop!
    check_if_files_are_in_correct_json_format()

    # Get the list of aircraft objects and its file locations
    aircraft_objects: list[dict[str, str]] = get_aircraft_objects_from_xsb_file(searchpath=CSL_PATH)

    # Special actions first!
    if args.undo:  # Undo changes, recover object from backup.
        recover_from_backup(aircraft_objects, STOP_ON_ERROR)
        sys.exit()

    if args.remove_backups:  # Remove the backupfiles.
        remove_backups(aircraft_objects)

    # Start of main processing
    log.info("Creating backups!")
    make_backup(aircraft_objects=aircraft_objects, stop_on_error=STOP_ON_ERROR)

    log.info(
        "Removing possible xpmp2 files as they can 'cache' the objects. They should be recreated on the fly while you use X-Plane."
    )
    remove_xpmp2_files(filepath=CSL_PATH)

    log.info(
        "Start processing! Duration depends on number of files and of course general hardware performance."
    )
    process_object_files(aircraft_objects)

    copy_new_to_old(aircraft_objects)

    log.info(f"Processing done, {len(aircraft_objects)} files have been processed!")

if __name__ == "__main__":
    args = parse_args()
    csl_path, stop_on_error = set_config(args.csl_path)
    main(args, csl_path, stop_on_error)
