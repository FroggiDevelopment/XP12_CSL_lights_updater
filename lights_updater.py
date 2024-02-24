from pathlib import Path
from helpers import make_backup
from helpers import determine_light_params
from typing import NoReturn

filepath = "./CSL"
# Old params
LIGHT_NEEDLES = [
    " airplane_landing",
    " airplane_taxi",
    " airplane_nav_left",
    " airplane_nav_right",
    " airplane_nav_tail",
    " airplane_strobe",
    " airplane_beacon",
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
    # xp12_params: str = determine_light_params(aircraft_type)

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
                        for [light in line for light in LIGHT_NEEDLES]:
                            print ("Line with aircraft lights of type:", light)
                        if "airplane_landing" in line:
                            line = line.replace(lighttype, f"{lighttype}_pm").replace(
                                "\n", ""
                            )
                            line += xp12_params
                        else:
                            line = line.replace(lighttype, f"{lighttype}_pm")
                    cached_line = line
                    print(cached_line)
            if line.startswith("LIGHT_SPILL_CUSTOM"):
                # print(f"cached line from above: {cached_line}")
                # print(line)
                if cached_line != "":
                    line = cached_line.replace("_pm", "_bb")
                    # print("Line after change:", line)
                    cached_line = ""
            new_obj_file.write(line)
            cached_line = ""  # necessary or not?


def main():
    for file in get_object_files(filepath):
        make_backup(file, ".obj.BCK")
        process_obj_file(file)


if __name__ == "__main__":
    main()
