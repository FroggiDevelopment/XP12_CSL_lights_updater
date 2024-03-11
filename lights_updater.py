import sys
import argparse
import logging
from pathlib import Path
from typing import NoReturn
from configparser import ConfigParser
from datetime import datetime

from helpers import make_backup
from helpers import delete_backups
from helpers import recover_from_backup
from helpers import determine_light_params
from helpers import get_aircraft_objects_from_xsb_file

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

# TODO: !!! CONFIG HAS TO BE GLOBAL!!! Maybe...

DEBUG = False
TEMP_FILE_SUFFIX = ".TEMP"
BACKUP_SUFFIX = ".BCK"
IS_XCSL = False
DO_BACKUP = True
STOP_ON_ERROR = True
LIGHT_INDICATORS = ["LIGHT_NAMED", "LIGHT_SPILL_CUSTOM", "LIGHT_PARAM"]


def get_xsb_inventory(csl_path: str) -> list[str]:
    """A very chaotic way of getting the object file pathes.
        Doe to the very different ways it is handled, a lot if if work is needed.

    Args:
        csl_path (str): Path to start searching.
        IS_XCSL (bool, optional): Is het a X-CSL package? Defaults to False.

    Returns:
        list[str]: A list with filepaths to the object files.
    """
    aircraft_desc_files = list(Path(csl_path).rglob("xsb_aircraft.txt"))
    aircraft_object_files: list[str] = []

    for desc_file in aircraft_desc_files:
        parentdir = desc_file.parent.absolute()

        with open(desc_file, "r") as xsb_aircraft_file:
            for line in xsb_aircraft_file:
                if line.startswith("OBJ8 SOLID YES"):
                    if "png" in line:
                        object_file = line.split()[3].split(":")[1]
                        object_path = Path(parentdir, object_file)
                        if object_path not in aircraft_object_files:
                            aircraft_object_files.append(object_path)
    return aircraft_object_files


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


def handle_light_params(line: str, lighttype: str, aircraft_type: str) -> str:
    """
    Create a new param line based on XP12 specifications, aircraft_type and lighttype

    Args:
        line (str): light params line old style
        lighttype (str): the type of light, e.g. airplane_beacon or airplane_landing
        aircraft_type (str): the type of the specific aircraft in ICAO terms. e.g. B733 for Boeing 737-300

    Returns:
        str: new line with updated params
    """
    new_line: str = ""

    # TODO: X-CSL could hide more surprises... must be checked.
    # There are special lights in the "old" style of obj files. A qick and dirty way to handle
    # this is below....
    lights_to_ignore = [
        "headlight",
        "_size",
        "_sp",
        "_pm",
        "_bb",
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

    if any(unwanted in line for unwanted in lights_to_ignore):
        return line

    line = filter_unwanted_light_params(line).replace("\n", "")
    logging.debug(f"Line created by filter_unwanted_light_params is: {line}")

    xp12_params: str = determine_light_params(aircraft_type, lighttype)
    if xp12_params != "" and line != "":
        line += f" {xp12_params}\n"

    # add pm to light param
    line = line.replace(lighttype, lighttype + "_pm")

    line += line.replace("_pm", "_bb")
    return line


def change_light_params(line: str, aircraft_type: str) -> str:
    """Changes the light parameters to XP12 specs

    Args:
        line (str): A string with light specifics parameters
        aircraft_type (): A string with the aircraft type

    Returns:
        str: A line with updated light parameters
    """
    if "LIGHT_NAMED" in line or "LIGHT_PARAM" in line:
        line = line.replace("LIGHT_NAMED", "LIGHT_PARAM")  # Change to new notation
        if [lighttype in line for lighttype in LIGHT_NEEDLES]:
            lighttype = line.split()[1]
            return handle_light_params(line, lighttype, aircraft_type)  # Set new params
    elif line.startswith("LIGHT_SPILL_CUSTOM"):  # Remove the old custom spill.
        return ""


def check_for_light_params(line: str, needles: list[str]) -> bool:
    """Checks if the line conatains any light parameters based on the start fo the line

    Args:
        line (str): A line from the aircraft object file

    Returns:
        bool: True if its a lightparam line
    """
    if any(light_indicator in line for light_indicator in needles):
        return True

    return False


def process_obj_file(aircraft_obj_file: Path) -> NoReturn:
    """Create new aircraft obj file with X-Plane 12 light params

    Args:
        file (Path): the existing aircraft object file
    """
    temp_object_file: Path = aircraft_obj_file.with_suffix(TEMP_FILE_SUFFIX)
    aircraft_type: str = aircraft_obj_file.name.split("_")[0]
    with open(aircraft_obj_file) as aircraft_object_file, open(
        temp_object_file, "w+"
    ) as new_obj_file:
        if DEBUG == True:
            logging.debug(f"Processing {aircraft_object_file.name}")
        for line in aircraft_object_file:
            if check_for_light_params(line, LIGHT_INDICATORS) == True:
                line = change_light_params(line, aircraft_type)
            new_obj_file.write(line)


def copy_new_to_old(files: list[Path]) -> NoReturn:
    """Copy the new created file over the original file
    Delete the new file
    """
    logging.debug("Start copying processed files to original file!")
    print("Start copying processed files to original file!")
    for file in files:
        destination_file = file.with_suffix(".obj")
        temp_object_file = file.with_suffix(TEMP_FILE_SUFFIX)
        print(f"Copying {temp_object_file.name} to {file} file!")
        logging.info(f"Copying {temp_object_file.name} to {file} file!")
        try:
            destination_file.write_bytes(temp_object_file.read_bytes())
        except PermissionError as err:
            if STOP_ON_ERROR == True:
                logging.error("Stopping on error!", err)
                sys.exit()
            continue
        try:
            temp_object_file.unlink()
        except PermissionError as err:
            logging.error(f"{temp_object_file.name} can not be deleted!", err)
            if STOP_ON_ERROR == True:
                sys.exit()
        logging.debug(f"Copy {file.name} to original object file done!")


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - (%(asctime)s) at line: %(lineno)d [%(filename)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="lights_updater.log",
        filemode="w",
    )
    start_time = datetime.now()

    # Get config
    config = ConfigParser()
    config.read("config.ini")

    # Set config(s)
    DEBUG = config.getboolean("generic", "debug")
    CSL_PATH = config["csl"]["csl_path"]
    IS_XCSL = config.getboolean("csl", "is_xcsl")
    DO_BACKUP = config.getboolean("generic", "do_backup")
    STOP_ON_ERROR = config.getboolean("generic", "STOP_ON_ERROR")
    # unwanted_lights = config["data"]["unwanted_lights"]

    # Check if cli params are present TODO: argparser???
    parser = argparse.ArgumentParser(
        prog="lights_updater.py",
        description="This programm can convert XP11 lightparams to the new XP12 specifications\
        It is mainly developed for LifeTraffic CSL aircraft.",
        epilog="No you know!",
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

    # Get the list of aircraft obj files and the number of files
    aircraft_objects = get_aircraft_objects_from_xsb_file(CSL_PATH, IS_XCSL)
    number_of_objects = len(aircraft_objects)

    # Start of actions based on cli arguments
    if args.undo:  # Undo changes, recover object from backup.
        print("Recovery activated!")
        logging.info("Recovery activated!")
        recover_from_backup(
            files=aircraft_objects,
            stop_on_error=STOP_ON_ERROR,
        )
        sys.exit()

    if args.remove_backups:  # Remove the backupfiles.
        print("Backups will be removed now!")
        yes_no = input("Are you sure? [yes/No]" or "No")
        if yes_no.lower() == "yes" or yes_no.lower() == "y":
            print("Okay! Let's do it....!!")
            delete_backups(aircraft_objects, BACKUP_SUFFIX)
        sys.exit()

    # Start of normal execution
    if DO_BACKUP == True:
        print("Creating backups!")
        logging.info("Creating backups!")
        make_backup(
            files=aircraft_objects,
            stop_on_error=STOP_ON_ERROR,
        )

    # Lets do the magic stuff!
    print(
        "Start processing! Duration depends on number of files and of course general hardware performance."
    )
    logging.info("Start processing!")
    for file in aircraft_objects:
        if DEBUG == True:
            print(f"Processing {file}")
        process_obj_file(file)

    copy_new_to_old(aircraft_objects)

    end_time = datetime.now()
    duration = end_time - start_time
    print(f"Processing done, {number_of_objects} files have been processed!")
    logging.info(f"Processing done, {number_of_objects} files have been processed!")
    print(f"It took {duration.seconds:.2f} seconds!")
    logging.info(f"It took {duration.seconds:.2f} seconds!")


if __name__ == "__main__":
    main()
