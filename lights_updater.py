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
SPILL_NEEDLE = "LIGHT_SPILL_CUSTOM"
LIGHT_REPLACE = {"old": "LIGHT_NAMED", "new": "LIGHT_PARAM"}
NEW_FILE_EXTENSION = ".obj.NEW"


def get_object_files(filepath: str) -> list:
    """Get all object files within filepath

    Args:
        filepath (str): Directory at wchich to start searching

    Returns:
        list: Of matching files
    """
    return list(Path(filepath).rglob("*.[oO][bB][jJ]"))


def update_block(anim_block: str):
    """Inspect this block and set new params per light type

    Args:
        anim_block (str): "Animation Block" with light params

    Returns:
        str: "Animation Block" with new XP12 light params
    """

    anim_block = anim_block.replace("LIGHT_NAMED", "LIGHT_PARAM")
    print(anim_block)
    return anim_block


def create_anim_block(aircraft_object: Path) -> str:
    """Create the anime start until anim end block for investigation

    Args:
        aircraft_object (Path): path to aircraft obj file

    Returns:
        str: Contains the full block between ANIM_start and ANIM_end
    """
    anim_block = ""
    new_data = ""
    copy = False
    block_end = False
    for line in aircraft_object:
        if line.startswith("ANIM_begin"):
            copy = True
            anim_block += line
        elif line.startswith("ANIM_end"):
            copy = False
            block_end = True
            anim_block += line
        elif block_end == True:
            if any(light in anim_block for light in LIGHT_NEEDLES):
                new_data += update_block(anim_block)
                anim_block = ""
            else:
                anim_block = ""
                continue
        elif copy == True:
            anim_block += line
        return new_data


def create_new_object_file(aircraft_object_file: Path) -> NoReturn:
    """Create new aircraft obj file with X-Plane 12 light params

    Args:
        file (Path): the existing aircraft object file
    """

    new_obj_file = aircraft_object_file.with_suffix(".obj.NEW")
    if new_obj_file.exists():
        new_obj_file.unlink()
    with (
        open(aircraft_object_file, "r") as aircraft_object,
        open(new_obj_file, "a") as new_aircraft_object,
    ):
        anim_block = create_anim_block(aircraft_object)
        if anim_block is not None:
            new_aircraft_object.write(anim_block)


def main():
    for file in get_object_files(filepath):
        make_backup(file, ".obj.BCK")
        create_new_object_file(file)


if __name__ == "__main__":
    main()
