from pathlib import Path
from helpers import make_backup

filepath = "/media/froggi/Flightsim/X-Plane 12/Resources/plugins/LiveTraffic/Resources/CSL/BB_Boeing/B773"
# Old params
NEEDLES = ("LIGHT_NAMED airplane_landing", "LIGHT_SPILL_CUSTOM")
NEW_FILE_EXTENSION = ".obj.NEW"
LIGHT_JETS = ("B733", "B734", "B737", "B738", "B739", "A318", "A319", "A320", "A321")
HEAVY_JETS = (
    "B717",
    "B744",
    "B74F",
    "B752",
    "B763",
    "B772",
    "B773",
    "B77L",
    "B77W",
    "B788",
    "A306",
    "A310",
    "A332",
    "A333",
    "A337",
    "A342",
    "A343",
    "A345",
    "A346",
    "A359",
    "A388",
)

# TODO: Navlights, Strobes, Beacon, Taxi


# temporary new light parameters
def determine_light_params(aircraft_type: str) -> str:
    """Determines the paramaters for the give aircraft type

    Args:
        aircraft_type (str): Aircraft type e.g. B733 for Boeing 737-300

    Returns:
        str: A string with the corresponding light parameters for the given aircraft type
    """
    if aircraft_type in HEAVY_JETS:
        return "0.76052475 0.65837479 0.57758057 3 765000cd 0.034766696 -0.052357007 -0.99802303 0.97992471"
    if aircraft_type in LIGHT_JETS:
        return "0.76052475 0.65837479 0.57758057 3 200000cd 0.034766696 -0.052357007 -0.99802303 0.97992471"


def process_line(line: str, xp12_params: str) -> str:
    """Process line to look for landing lights or spill entry and replace with new params

    Args:
        line (str): line from aircarft object file
        xp12_params (str): _description_

    Returns:
        str: _description_
    """

    # New
    new_landing_light_params = "LIGHT_PARAM airplane_landing_pm"
    new_landing_light_billboard_params = "LIGHT_PARAM airplane_landing_bb"

    if line.startswith(NEEDLES[0]):
        print("##################### SPILL-LIGHT ##################")
        print("Spill:", line)
        new_spill_line = line.replace(
            NEEDLES[0], new_landing_light_billboard_params
        ).replace("\n", "")
        new_spill_line += f" {xp12_params}\n"
        print("New Spill:", new_spill_line)
        print("################### END SPILL-LIGHT ################")
        return new_spill_line
    if line.startswith(NEEDLES[1]):  # TODO: new syntax
        print("--------------------- LANDING-LIGHTS -----------------")
        print("Old landinglights:", line.replace("\n", "").split(" "))
        # try:
        #     [light_param, light_name, lat, long, height] = line.replace("\n", "").split(
        #         " "
        #     )
        # except ValueError as err:
        #     print(err)

        new_line = line.replace(NEEDLES[1], new_landing_light_params).replace("\n", "")
        new_line += f" {xp12_params}\n"
        print("New landinglights:", new_line)
        print("------------------------------------------------------")
        return new_line
    # return line


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
        make_backup(file)
        create_new_object_file(file)


if __name__ == "__main__":
    main()
