from pathlib import Path
from helpers import make_backup
from helpers import determine_light_params

filepath = "./CSL/BB_Boeing/B773"
# Old params
LIGHT_NEEDLES = (
    "airplane_landing",
    "airplane_taxi",
    "airplane_nav_left",
    "airplane_nav_right",
    "airplane_nav_tail",
    "airplane_strobe",
    "airplane_beacon",
)
SPILL_NEEDLE = "LIGHT_SPILL_CUSTOM"
LIGHT_REPLACE = {"old": "LIGHT_NAMED", "new": "LIGHT_PARAM"}
NEW_FILE_EXTENSION = ".obj.NEW"


def process_line(line: str, xp12_params: str) -> str:
    """Process line to look for landing lights or spill entry and replace with new params

    Args:
        line (str): line from aircarft object file
        xp12_params (str): _description_

    Returns:
        str: _description_
    """

    # Replace OLD with NEW lightparam name
    linestart = (
        " ".join(line.split()[:1])
        .replace(LIGHT_REPLACE["old"], LIGHT_REPLACE["new"])
        .replace(SPILL_NEEDLE, LIGHT_REPLACE["new"])
    )

    line = line.replace(LIGHT_REPLACE["old"], "")

    light_type = " ".join(line.split()[:1])

    # line = line.replace(light_type, "")

    # New light params
    new_light_suffix = "_pm"
    new__billboard_suffix = "_bb"

    xyz_light_coordinates = " ".join(line.split()[:3])

    # Check if line starts with SPILL_NEEDLE
    if line.startswith(SPILL_NEEDLE):
        print("##################### SPILL-LIGHT ##################")
        print("Spill:", line)
        new_spill_line = line.replace(
            SPILL_NEEDLE,
        ).replace("\n", "")
        new_spill_line += f" {xp12_params}\n"
        print("New Spill:", new_spill_line)
        print("################### END SPILL-LIGHT ################")
        print(f"{linestart} {light_type}_bb {new_spill_line}")
        return f"{linestart} {light_type}_bb {new_spill_line}"

    # Check if linestart is in LIGHT_NEEDLES tuple
    if " ".join(line.split()[:1]) in LIGHT_NEEDLES:
        print("--------------------- LANDING-LIGHTS -----------------")
        print("Old landinglights:", line.replace("\n", "").split(" "))
        new_line = xyz_light_coordinates.replace(
            LIGHT_REPLACE["old"], new_landing_light_params
        ).replace("\n", "")
        new_line += f" {xp12_params}\n"
        print("New landinglights:", new_line)
        print("------------------------------------------------------")
        print(f"{linestart} {light_type}_pm {new_line}")
        return f"{linestart} {light_type}_pm {new_line}"


def get_object_files(filepath: str) -> list:
    """Get all object files within filepath

    Args:
        filepath (str): Directory at wchich to start searching

    Returns:
        list: Of matching files
    """
    return list(Path(filepath).rglob("*.[oO][bB][jJ]"))


def create_new_object_file(aircraft_object_file: Path) -> None:
    """Create new aircraft obj file with X-Plane 12 light params

    Args:
        file (Path): the existing aircraft object file
    """
    new_file = aircraft_object_file.with_suffix(NEW_FILE_EXTENSION)

    if new_file.exists():
        new_file.unlink()

    with open(aircraft_object_file) as aircraft_object:
        aircraft_type = str(aircraft_object_file.parents[0]).split("/")[-1]
        xp12_params = determine_light_params(aircraft_type)

        for line in aircraft_object:
            with open(new_file, "a") as new_obj_file:
                if line.startswith(LIGHT_REPLACE["old"]) or line.startswith(
                    SPILL_NEEDLE
                ):
                    newline = process_line(line, xp12_params)
                    new_obj_file.write(newline)
                    continue
                new_obj_file.write(line)


def main():
    for file in get_object_files(filepath):
        make_backup(file, ".obj.backup")
        create_new_object_file(file)


if __name__ == "__main__":
    main()
