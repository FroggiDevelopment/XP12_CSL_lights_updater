from pathlib import Path
from helpers import make_backup
from helpers import determine_light_params
from typing import NoReturn

filepath = "./CSL"
# filepath = "/media/froggi/Flightsim/X-Plane 12/Resources/plugins/LiveTraffic/Resources/CSL/BB_Boeing/B738"
# Old params
LIGHT_NEEDLES: list[str] = [
    "airplane_landing",
    "airplane_taxi",
    "airplane_nav_left",
    "airplane_nav_right",
    "airplane_nav_tail",
    "airplane_strobe",
    "airplane_beacon",
]


def get_object_files(filepath: str) -> list:
    """Get all object files within filepath using rglob
       and a pattern to search for. In this case all obj
       files. Hardcoded patern!

    Args:
        filepath (str): Directory at which to start searching

    Returns:
        list: Of matching filepathes
    """
    return list(Path(filepath).rglob("*.[oO][bB][jJ]"))


def handle_special_cases(aircraft_lightparams_line: str) -> str:
    """
    In case of special lines, e.g. missing SPILL, new param names,
    handle these cases here.
    As it seems are the SPILLS fro some lights missing.
    This function takes care of these cases.


    Args:
        aircraft_lightparams_line (str): aircraft_lightparams_line with light params

    Returns:
        str: aircraft_lightparams_line with updated params according the the specifications
             in XP12
    """
    handled_line = ""
    if "airplane_nav" in aircraft_lightparams_line:
        handled_line = (
            aircraft_lightparams_line.replace("_left", "")
            .replace("_right", "")
            .replace("_tail", "")
        )
    else:
        return aircraft_lightparams_line
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


def handle_light_params(
    aircraft_lightparams_line: str, lighttype: str, aircraft_type: str
) -> str:
    """
    Create a new param aircraft_lightparams_line based on XP12 specifications, aircraft_type and lighttype

    Args:
        aircraft_lightparams_line (str): light params line old style
        lighttype (str): the type of light, e.g. airplane_beacon or airplane_landing
        aircraft_type (str): the type of the specific aircraft in ICAO terms. e.g. B733 for Boeing 737-300

    Returns:
        str: new line with updated params
    """
    new_line: str = ""
    xp12_params: str = determine_light_params(aircraft_type, lighttype)

    if "headlight" in aircraft_lightparams_line:  # Filter unusual lighttype names
        aircraft_lightparams_line = ""
        lighttype = "airplane_landing"

    new_line = create_new_light_name(aircraft_lightparams_line, lighttype)

    if xp12_params[lighttype] != "" and aircraft_lightparams_line != "":
        new_line += f" {xp12_params[lighttype]}\n"

    new_line = handle_special_cases(new_line)
    new_line += new_line.replace("_pm", "_bb")
    return new_line


def process_obj_file(aircraft_obj_file: Path) -> NoReturn:
    """Create new aircraft obj file with X-Plane 12 light params

    Args:
        file (Path): the existing aircraft object file
    """
    new_object_file: Path = aircraft_obj_file.with_suffix(".obj.NEW")
    aircraft_type: str = aircraft_obj_file.name.split("_")[0]

    # Delete new file to start a clean build.
    if new_object_file.exists():
        new_object_file.unlink()

    with open(aircraft_obj_file) as aircraft_object_file, open(
        new_object_file, "w+"
    ) as new_obj_file:
        for aircraft_lightparams_line in aircraft_object_file:
            if aircraft_lightparams_line.startswith("LIGHT_NAMED"):
                aircraft_lightparams_line = aircraft_lightparams_line.replace(
                    "LIGHT_NAMED", "LIGHT_PARAM"
                )

                if [
                    lighttype in aircraft_lightparams_line
                    for lighttype in LIGHT_NEEDLES
                ]:
                    lighttype = aircraft_lightparams_line.split(" ")[1]

                    aircraft_lightparams_line = handle_light_params(
                        aircraft_lightparams_line, lighttype, aircraft_type
                    )

            if aircraft_lightparams_line.startswith("LIGHT_SPILL_CUSTOM"):
                aircraft_lightparams_line = ""
            # Write data to new object file
            new_obj_file.write(aircraft_lightparams_line)


def copy_new_to_old() -> NoReturn:
    """Copy the new created file over the original file
    Delete the new file
    """
    files_to_copy = list(Path(filepath).rglob("*.NEW"))

    for file in files_to_copy:
        new_object_file = file.with_suffix("")
        new_object_file.write_bytes(file.read_bytes())
        file.unlink()


def main() -> None:
    for file in get_object_files(filepath):
        make_backup(file, ".obj.BCK")
        process_obj_file(file)
    # copy_new_to_old()


if __name__ == "__main__":
    main()
