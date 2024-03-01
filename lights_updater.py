from pathlib import Path
from helpers import make_backup
from helpers import recover_from_backup
from helpers import determine_light_params
from typing import NoReturn
from configparser import ConfigParser
import sys

LIGHT_NEEDLES: list[str] = [
    "airplane_landing",
    "airplane_taxi",
    "airplane_nav_left",
    "airplane_nav_right",
    "airplane_nav_tail",
    "airplane_strobe",
    "airplane_beacon",
]


def adapt_nav_lights(line: str, old_nav_lights: list[str]) -> str:
    """Delete unused parameter parts and return new string

    Args:
        line (str): Line with aircraft navlight parameter
        to_correct_list (list): List of items to be removed

    Returns:
        str: Line without unused parameter(-parts)
    """
    for item in old_nav_lights:
        line = line.replace(item, "")

    return line


def get_object_files(csl_path: str) -> list[Path]:
    """Get all object files within csl_path using rglob
       and a pattern to search for. In this case all obj
       files. Hardcoded patern!

    Args:
        csl_path (str): Directory at which to start searching

    Returns:
        list: Of matching filepathes
    """
    return list(Path(csl_path).rglob("*.[oO][bB][jJ]"))


def handle_special_cases(line: str) -> str:
    """
    In case of special lines, e.g. missing SPILL, new param names,
    handle these cases here.
    As it seems are the SPILLS fro some lights missing.
    This function takes care of these cases.


    Args:
        line (str): line with light params

    Returns:
        str: line with updated params according the the specifications
             in XP12
    """
    handled_line = ""
    if "airplane_nav" in line:
        handled_line = adapt_nav_lights(line, ["_left", "_right", "_tail"])
    else:
        return line
    return handled_line


def create_new_light_name(line: str, lighttype: str) -> str:
    """Takes the original line and adds _pm to the light name
       of type {lighttype}

    Args:
        line (str): The original line with the old light params
        lighttype (str): the type of light that needs updating

    Returns:
        str: New line with updated light name
    """
    return line.replace(lighttype, f"{lighttype}_pm").rstrip("\n")


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
    xp12_params: str = determine_light_params(aircraft_type, lighttype)

    if "headlight" in line:  # Filter unusual lighttype names
        line = ""
        lighttype = "airplane_landing"

    new_line = create_new_light_name(line, lighttype)

    if xp12_params[lighttype] != "" and line != "":
        new_line += f" {xp12_params[lighttype]}\n"

    new_line = handle_special_cases(new_line)
    new_line += new_line.replace("_pm", "_bb")
    return new_line


def change_light_params(line: str, aircraft_type: str) -> str:
    """Changes the light parameters to XP12 specs

    Args:
        line (str): A string with light specifics parameters
        aircraft_type (): A string with the aircraft type

    Returns:
        str: A line with updated light parameters
    """
    if line.startswith("LIGHT_NAMED"):
        line = line.replace("LIGHT_NAMED", "LIGHT_PARAM")  # Change to new notation
        if [lighttype in line for lighttype in LIGHT_NEEDLES]:
            lighttype = line.split(" ")[1]

            line = handle_light_params(line, lighttype, aircraft_type)  # Set new params
    elif line.startswith("LIGHT_SPILL_CUSTOM"):  # Remove the old custom spill.
        line = ""

    return line


def check_for_light_params(line: str) -> bool:
    """Checks if the line conatains any light parameters based on the start fo the line

    Args:
        line (str): A line from the aircraft object file

    Returns:
        bool: True if its a lightparam line
    """
    is_light_line: bool = False
    if line.startswith("LIGHT_NAMED") or line.startswith("LIGHT_SPILL_CUSTOM"):
        is_light_line = True

    return is_light_line


def delete_file(file: Path):
    if file.exists():
        file.unlink()


def process_obj_file(aircraft_obj_file: Path) -> NoReturn:
    """Create new aircraft obj file with X-Plane 12 light params

    Args:
        file (Path): the existing aircraft object file
    """
    new_object_file: Path = aircraft_obj_file.with_suffix(".NEW")
    aircraft_type: str = aircraft_obj_file.name.split("_")[0]

    # Delete new file to start a clean build.
    delete_file(new_object_file)

    with open(aircraft_obj_file) as aircraft_object_file, open(
        new_object_file, "w+"
    ) as new_obj_file:
        for line in aircraft_object_file:
            if check_for_light_params(line) == True:
                line = change_light_params(line, aircraft_type)
            new_obj_file.write(line)


def copy_new_to_old(*, filepath: Path, stop_on_error: bool = True) -> NoReturn:
    """Copy the new created file over the original file
    Delete the new file
    """
    files_to_copy = list(Path(filepath).rglob("*.NEW"))

    for file in files_to_copy:
        new_object_file = file.with_suffix(".obj")

        try:
            new_object_file.write_bytes(file.read_bytes())
        except PermissionError as err:
            if stop_on_error == True:
                print("Stopping on error!", err)
                sys.exit()
            continue
        file.unlink()


def main() -> None:
    # Get config
    config = ConfigParser()
    config.read("./config.ini")

    # Set config(s)
    CSL_PATH = config["CSL"]["csl_path"]
    do_backup = config.getboolean("generic", "do_backup")
    backup_extension = config["generic"]["backup_extension"]
    stop_on_error = config.getboolean("generic", "stop_on_error")

    # Get all aircraft obj files
    aircraft_objects = get_object_files(CSL_PATH)

    if len(sys.argv) > 1:
        if sys.argv[1] == "-r":
            print("Recovery activated!")
            recover_from_backup(
                files=aircraft_objects,
                backup_extension=backup_extension,
                stop_on_error=stop_on_error,
            )

    if do_backup == True:
        print("Creating backups!")
        make_backup(
            files=aircraft_objects,
            backup_extension=backup_extension,
            stop_on_error=stop_on_error,
        )

    # Lets do the magic stuff!
    for file in aircraft_objects:
        process_obj_file(file)
    copy_new_to_old(filepath=CSL_PATH, stop_on_error=stop_on_error)


if __name__ == "__main__":
    main()
