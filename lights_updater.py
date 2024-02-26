from pathlib import Path
from helpers import make_backup
from helpers import determine_light_params
from typing import NoReturn

filepath = "./CSL"
# filepath = "/media/froggi/Flightsim/X-Plane 12/Resources/plugins/LiveTraffic/Resources/CSL/BB_Boeing/B738"
# Old params
LIGHT_NEEDLES = [
    "airplane_landing",
    "airplane_taxi",
    "airplane_nav_left",
    "airplane_nav_right",
    "airplane_nav_tail",
    "airplane_strobe",
    "airplane_beacon",
]


def get_object_files(filepath: str) -> list:
    """Get all object files within filepath

    Args:
        filepath (str): Directory at which to start searching

    Returns:
        list: Of matching files
    """
    return list(Path(filepath).rglob("*.[oO][bB][jJ]"))


def handle_special_cases(line: str) -> str:
    """
    In case of special lines, e.g. missing SPILL, new param names,
    handle these cases here.
    As it seems are the SPILLS fro some lights missing.
    This function takes care of these cases.


    Args:
        line (str): line with light params

    Returns:
        str: Line with updated params according the the specifications
             in XP12
    """
    handled_line = ""
    if "airplane_nav" in line:
        handled_line = (
            line.replace("_left", "").replace("_right", "").replace("_tail", "")
        )
    elif "airplane_beacon" in line:
        handled_line += line.replace("_pm", "_bb")
    elif "airplane_strobe" in line:
        handled_line += line.replace("_pm", "_bb")
    else:
        return line
    return handled_line


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
    print("Inside handling:", lighttype)
    xp12_params: str = determine_light_params(aircraft_type, lighttype)
    new_line = line.replace(lighttype, f"{lighttype}_pm").replace("\n", "")

    if xp12_params[lighttype] != "":
        new_line += f" {xp12_params[lighttype]}\n"

    new_line = handle_special_cases(new_line)

    return new_line


def process_obj_file(aircraft_obj_file: Path) -> NoReturn:
    """Create new aircraft obj file with X-Plane 12 light params

    Args:
        file (Path): the existing aircraft object file
    """

    cached_line: str = ""
    new_object_file: Path = aircraft_obj_file.with_suffix(".obj.NEW")
    aircraft_type = aircraft_obj_file.name.split("_")[0]

    # Delete new file to start a clean build.
    if new_object_file.exists():
        new_object_file.unlink()

    with open(aircraft_obj_file) as aircraft_object_file, open(
        new_object_file, "w+"
    ) as new_obj_file:
        for line in aircraft_object_file:
            if line.startswith("LIGHT_NAMED"):
                line = line.replace("LIGHT_NAMED", "LIGHT_PARAM")

                if [lighttype in line for lighttype in LIGHT_NEEDLES]:
                    lighttype = line.split(" ")[1]

                    if lighttype == "headlight":  # Filter unusual lighttype names
                        line.replace("headlight", "airplane_landing")

                    line = handle_light_params(line, lighttype, aircraft_type)
                    cached_line = line
                    
            if line.startswith("LIGHT_SPILL_CUSTOM"):
                if cached_line != "":
                    line = cached_line.replace("_pm", "_bb")
                    cached_line = ""
                else:
                    line = line.replace("LIGHT_SPILL_CUSTOM", "LIGHT_PARAM")
                    line = line.replace("_pm", "_bb")
            # Write data to new object file
            new_obj_file.write(line)


def copy_new_to_old() -> NoReturn:
    """Copy the new created file over the original file
    Delete the new file
    """
    files_to_copy = list(Path(filepath).rglob("*.NEW"))

    for file in files_to_copy:
        new_object_file = file.with_suffix("")
        new_object_file.write_bytes(file.read_bytes())
        file.unlink()


def main():
    for file in get_object_files(filepath):
        make_backup(file, ".obj.BCK")
        process_obj_file(file)
    # copy_new_to_old()


if __name__ == "__main__":
    main()
