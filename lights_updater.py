#!/usr/bin/env python3
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
from pathlib import Path
from configparser import ConfigParser

from helpers import make_backup
from helpers import delete_backups
from helpers import recover_from_backup
from helpers import remove_xpmp2_files
from helpers import get_light_params_for_aircraft_type
from helpers import get_aircraft_objects_from_xsb_file

from decorators.time_benchmark import time_benchmark

TEMP_FILE_SUFFIX: str = ".TEMP"
BACKUP_SUFFIX: str = ".BCK"
DO_BACKUP: bool = True
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
]

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(name)-12s: %(levelname)-8s - (%(asctime)s) at line: %(lineno)d [%(filename)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="lights_updater.log",
    filemode="w",
)
# Add screen handler
screen = logging.StreamHandler()
screen.setLevel(logging.INFO)
screenformatter = logging.Formatter("%(name)-12s: %(levelname)-8s - %(message)s")
screen.setFormatter(screenformatter)

logging.getLogger().addHandler(screen)

log = logging.getLogger("lights_updater")


def filter_unwanted_light_params(line: str) -> str:
    """Filter out light params that are old or otherwise wrong.
       Can be expanded for future cases.

    Args:
        line (str): Line with light parameters

    Returns:
        str: Corrected line with light parameters
    """

    # Some lines are commented out... Must be undone
    if "#LIGHT_PARAM" in line:
        line = line.replace("#LIGHT_PARAM", "LIGHT_PARAM")

    if "airplane_nav" in line:
        for item in ["_left", "_right", "_tail"]:
            line = line.replace(item, "")

    return line


def ignore_line(line: str) -> bool:
    """Test if line contains ignorable light parameters

    Args:
        line (str): String of light parameters

    Returns:
        bool: True if it can be ignored, False otherwise.
    """
    lights_to_ignore = [
        "headlight",
        "_size",
        "_sp",
        "taillight",
        "_rotate",
        "_core",
        "_size",
        "_omni",
        "_dir",
        "airplane_strobe_omni",
        "full_custom_halo_night",
        "_glow",
        "_flare",
        "logo",
    ]

    if any(to_ignore in line for to_ignore in lights_to_ignore):
        return True
    return False


def process_lights(line: str, light_params: dict[str, str]) -> str:
    """Changes the light parameters to XP12 specs

    Args:
        line (str): A string with light specifics parameters
        light_params (dict[str, str]): A dictionary with the light parameters

    Returns:
        str: A line with updated light parameters
    """
    # Just in case _pm and / or _bb are already defined, return the line unmodified
    if any(new_light_param in line for new_light_param in ["_pm", "_bb"]):
        return line
    lighttype = line.split()[1]
    line = line.replace("\n", "")
    line += f" {light_params[lighttype]}\n"
    line = line.replace("LIGHT_NAMED", "LIGHT_PARAM")  # Change to new notation
    line = line.replace(f"{lighttype}", f"{lighttype}_pm")
    line += line.replace("_pm", "_bb")
    line = filter_unwanted_light_params(line)
    return line


@time_benchmark
def process_obj_file(aircraft_obj_file: Path) -> None:
    """Create new aircraft obj file with X-Plane 12 light params

    Args:
        file (Path): the existing aircraft object file
    """
    temp_object_file: Path = aircraft_obj_file.with_suffix(suffix=TEMP_FILE_SUFFIX)

    # If airline is in the filename, it is sparated by "_". The 'normal' case.
    if "_" in aircraft_obj_file.name:
        aircraft_type: str = aircraft_obj_file.name.split("_")[0]
    else:  # Rare case with only type in object name without airline abbreviation.
        aircraft_type = aircraft_obj_file.name.rstrip(".obj")

    light_params = get_light_params_for_aircraft_type(aircraft_type)

    try:
        with open(aircraft_obj_file) as aircraft_object_file, open(
            temp_object_file, "w+"
        ) as new_obj_file:
            log.info(f"Processing {aircraft_object_file.name}")
            for line in aircraft_object_file:
                if line.startswith("# "):
                    continue
                if ignore_line(line) is True:
                    continue
                if any(lighttype in line for lighttype in LIGHT_NEEDLES):
                    line = process_lights(line, light_params)

                new_obj_file.write(line)
    except FileNotFoundError as err:
        log.error(f"{aircraft_obj_file.name} not found!", err)
        if STOP_ON_ERROR is True:
            sys.exit()


def copy_new_to_old(files: list[Path]) -> None:
    """Copy the new created file over the original file
    Delete the new file
    """
    log.debug("Start copying processed files to original file!")
    log.info("Start copying processed files to original file!")
    for file in files:
        destination_file = file.with_suffix(".obj")
        temp_object_file = file.with_suffix(TEMP_FILE_SUFFIX)
        log.info(f"Copying {temp_object_file.name} to {file} file!")
        try:
            destination_file.write_bytes(temp_object_file.read_bytes())
        except PermissionError as err:
            if STOP_ON_ERROR is True:
                log.error("Stopping on error!", err)
                sys.exit()
            continue
        try:
            temp_object_file.unlink()
        except PermissionError as err:
            log.error(f"{temp_object_file.name} can not be deleted!", err)
            if STOP_ON_ERROR is True:
                sys.exit()
        log.debug(f"Copy {file.name} to original object file done!")


def set_config() -> tuple[str, bool, bool]:
    # Get config from file
    config = ConfigParser()
    config.read("configs/config.ini")

    # Set config(s)
    CSL_PATH = config["csl"]["csl_path"]
    DO_BACKUP = config.getboolean("generic", "do_backup")
    STOP_ON_ERROR = config.getboolean("generic", "STOP_ON_ERROR")

    return CSL_PATH, DO_BACKUP, STOP_ON_ERROR


@time_benchmark
def main() -> None:

    # Check if cli params are present
    parser = argparse.ArgumentParser(
        prog="lights_updater.py",
        description="This programm can convert XP11 lightparams to the new XP12 specifications.\n"
        "Developed for getting landing lights with LifeTraffic.\n"
        "Works only prtial woth custom CSL aircraft.",
        epilog="No you know!",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-u",
        "--undo",
        action="store_true",
        help="Rolls back the previous made changes!",
    )
    parser.add_argument(
        "-r",
        "--remove-backups",
        action="store_true",
        help="Removes the backup files. Be careful!",
    )
    args = parser.parse_args()

    # Set config
    CSL_PATH, DO_BACKUP, STOP_ON_ERROR = set_config()

    # Get the list of aircraft obj files and the number of files
    aircraft_objects: list[Path] = get_aircraft_objects_from_xsb_file(
        searchpath=CSL_PATH
    )
    number_of_objects = len(aircraft_objects)

    # Start of actions based on cli arguments
    if args.undo:  # Undo changes, recover object from backup.
        log.info("Recovery activated!")
        recover_from_backup(
            files=aircraft_objects,
            stop_on_error=STOP_ON_ERROR,
        )
        sys.exit()

    if args.remove_backups:  # Remove the backupfiles.
        log.info("Backups will be removed now!")
        yes_no = input("Are you sure? [yes/No]" or "No")
        if yes_no.lower() == "yes" or yes_no.lower() == "y":
            log.info("Okay! Let's do it....!!")
            delete_backups(files=aircraft_objects, backup_extension=BACKUP_SUFFIX)
        sys.exit()

    # Start of normal execution
    if DO_BACKUP is True:
        log.info("Creating backups!")
        make_backup(
            files=aircraft_objects,
            stop_on_error=STOP_ON_ERROR,
        )

    # Lets do the magic stuff!
    log.info(
        "Start processing! Duration depends on number of files and of course general hardware performance."
    )
    log.info(
        "Removing possible xpmp2 files as they can 'cache' the objects. LifeTraffic will recreate them."
    )

    remove_xpmp2_files(filepath=CSL_PATH)

    for file in aircraft_objects:
        process_obj_file(aircraft_obj_file=file)

    copy_new_to_old(aircraft_objects)

    log.info(f"Processing done, {number_of_objects} files have been processed!")


if __name__ == "__main__":
    main()
