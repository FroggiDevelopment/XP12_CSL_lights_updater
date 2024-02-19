from pathlib import Path
from helpers import make_backup
from helpers import determine_light_params

filepath = "/media/froggi/Flightsim/X-Plane 12/Resources/plugins/LiveTraffic/Resources/CSL/BB_Boeing/B773"
# Old params
NEEDLES = (
    "LIGHT_NAMED airplane_landing",
    "LIGHT_SPILL_CUSTOM",
    "LIGHT_NAMED airplane_taxi",
    "LIGHT_NAMED airplane_nav_left",
    "LIGHT_NAMED airplane_nav_right",
    "LIGHT_NAMED airplane_nav_tail",
)
NEW_FILE_EXTENSION = ".obj.NEW"

# TODO: Navlights, Strobes, Beacon, Taxi


def process_line(line: str, xp12_params: str) -> str:
    """Process line to look for landing lights or spill entry and replace with new params

    Args:
        line (str): line from aircarft object file
        xp12_params (str): _description_

    Returns:
        str: _description_
    """

    # New light params
    new_landing_light_params = "LIGHT_PARAM airplane_landing_pm"
    new_landing_light_billboard_params = "LIGHT_PARAM airplane_landing_bb"
    xyz_light_coordinates = " ".join(line.split()[:3])

    if line.startswith(NEEDLES[0]):
        print("##################### SPILL-LIGHT ##################")
        print("Spill:", line)
        new_spill_line = xyz_light_coordinates.replace(
            NEEDLES[0], new_landing_light_billboard_params
        ).replace("\n", "")
        new_spill_line += f" {xp12_params}\n"
        print("New Spill:", new_spill_line)
        print("################### END SPILL-LIGHT ################")
        return new_spill_line
    if line.startswith(NEEDLES[1]):
        print("--------------------- LANDING-LIGHTS -----------------")
        print("Old landinglights:", line.replace("\n", "").split(" "))
        new_line = xyz_light_coordinates.replace(
            NEEDLES[1], new_landing_light_params
        ).replace("\n", "")
        new_line += f" {xp12_params}\n"
        print("New landinglights:", new_line)
        print("------------------------------------------------------")
        return new_line


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
                if line.startswith(NEEDLES[0]) or line.startswith(NEEDLES[1]):
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
