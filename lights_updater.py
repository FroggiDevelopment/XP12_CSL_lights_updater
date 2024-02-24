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


# def update_block(anim_block: str):
#     """Inspect this block and set new params per light type

#     Args:
#         anim_block (str): "Animation Block" with light params

#     Returns:
#         str: "Animation Block" with new XP12 light params
#     """

#     anim_block = anim_block.replace("LIGHT_NAMED", "LIGHT_PARAM")
#     print(anim_block)
#     return anim_block


# def create_anim_block(aircraft_object: Path) -> str:
#     """Create the anime start until anim end block for investigation

#     Args:
#         aircraft_object (Path): path to aircraft obj file

#     Returns:
#         str: Contains the full block between ANIM_start and ANIM_end
#     """
#     anim_block = ""
#     new_data = ""
#     copy = False
#     block_end = False
#     for line in aircraft_object:
#         if line.startswith("ANIM_begin"):
#             copy = True
#             anim_block += line
#         elif line.startswith("ANIM_end"):
#             copy = False
#             block_end = True
#             anim_block += line
#         elif block_end == True:
#             if any(light in anim_block for light in LIGHT_NEEDLES):
#                 new_data += update_block(anim_block)
#                 anim_block = ""
#             else:
#                 anim_block = ""
#                 continue
#         elif copy == True:
#             anim_block += line
#     return new_data


def process_obj_file(aircraft_obj_file: Path) -> NoReturn:
    """Create new aircraft obj file with X-Plane 12 light params

    Args:
        file (Path): the existing aircraft object file
    """

    new_object_file: Path = aircraft_obj_file.with_suffix(".obj.NEW")
    cached_line: str = ""
    aircraft_type: str = str(aircraft_obj_file.parents[0]).split("/")[-1]
    xp12_params: str = determine_light_params(aircraft_type)
    aircraft_light_type: str = ""

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
                        if "airplane_landing" in line:
                            line = line.replace(lighttype, f"{lighttype}_pm").replace(
                                "\n", ""
                            )
                            line += xp12_params
                        else:
                            line = line.replace(lighttype, f"{lighttype}_pm")
                        cached_line = line
            if line.startswith("LIGHT_SPILL_CUSTOM"):
                line = cached_line.replace("_pm", "_bb")
            new_obj_file.write(line)
            cached_line = ""


def main():
    for file in get_object_files(filepath):
        make_backup(file, ".obj.BCK")
        process_obj_file(file)


if __name__ == "__main__":
    main()
