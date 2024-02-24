from pathlib import Path
from helpers import make_backup
from helpers import determine_light_params
from typing import NoReturn

filepath = "./CSL"
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


def process_obj_file(aircraft_obj_file: Path) -> NoReturn:
    """Create new aircraft obj file with X-Plane 12 light params

    Args:
        file (Path): the existing aircraft object file
    """

    new_object_file: Path = aircraft_obj_file.with_suffix(".obj.NEW")
    cached_line: str = ""
    aircraft_type: str = str(aircraft_obj_file.parents[0]).split("/")[-1]

    if new_object_file.exists():
        new_object_file.unlink()

    with open(aircraft_obj_file) as aircraft_object_file, open(
        new_object_file, "w+"
    ) as new_obj_file:
        for line in aircraft_object_file:
            if line.startswith("LIGHT_NAMED"):
                line = line.replace("LIGHT_NAMED", "LIGHT_PARAM")
                for lighttype in LIGHT_NEEDLES:
                    if lighttype in line:
                        xp12_params: str = determine_light_params(
                            aircraft_type, lighttype
                        )
                        line = line.replace(lighttype, f"{lighttype}_pm").replace(
                            "\n", ""
                        )
                        if xp12_params[lighttype] != "":
                            line += f" {xp12_params[lighttype]}"
                        if "airplane_nav" in line:
                            print("navlights found!")
                            line = (
                                line.replace("_left", "")
                                .replace("_right", "")
                                .replace("_tail", "")
                            )
                        cached_line = line
            if line.startswith("LIGHT_SPILL_CUSTOM"):
                if cached_line != "":
                    line = cached_line.replace("_pm", "_bb")
                    cached_line = ""
            new_obj_file.write(line)


def main():
    for file in get_object_files(filepath):
        make_backup(file, ".obj.BCK")
        process_obj_file(file)


if __name__ == "__main__":
    main()
