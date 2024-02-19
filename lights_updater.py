from pathlib import Path
from helpers import make_backup

filepath = "/media/froggi/Flightsim/X-Plane 12/Resources/plugins/LiveTraffic/Resources/CSL/BB_Boeing/B773"
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
    "A388",
)

# TODO: Navlights, Strobes, Beacon, Taxi

# Old spill-params:
# LIGHT_SPILL_CUSTOM, #
# x,
# y,
# z,
# r,
# g,
# b,
# brightness(set to 1),
# size in m,
# direction (hor, vert, lateral),
# semiwidth of lightcone,
# dataref

# New lightparams
# light_param,
# light_name,
# lat,
# long,
# height,
# r,
# g,
# b,
# light_index,
# candelar,
# vert_rotation,  # (left/right)
# lat_rotation,  # (up/down)
# for_aft_direction,
# cone_angle


# temporary new light parameters
def determine_light_params(aircraft_type):
    if aircraft_type in HEAVY_JETS:
        return "0.76052475 0.65837479 0.57758057 3 765000cd 0.034766696 -0.052357007 -0.99802303 0.97992471"
    if aircraft_type in LIGHT_JETS:
        return "0.76052475 0.65837479 0.57758057 3 200000cd 0.034766696 -0.052357007 -0.99802303 0.97992471"


def split_lines_into_params():
    pass


def process_line(line: str, xp12_params: str) -> str:
    """Get a line from a file, look for landing lights
    or spill entry and replace with new params

    Params:
    line: string 'line from obj-file'
    returns: string 'line with new params'
    """

    # Old
    needle = "LIGHT_NAMED airplane_landing"
    spill_needle = "LIGHT_SPILL_CUSTOM"

    # New
    new_landing_lights = "LIGHT_PARAM airplane_landing_pm"
    new_landing_lights_bb = "LIGHT_PARAM airplane_landing_bb"

    if spill_needle in line:
        print("##################### SPILL-LIGHT ##################")
        print("Spill:", line)
        new_spill_line = line.replace(spill_needle, new_landing_lights_bb).replace(
            "\n", ""
        )
        new_spill_line += f" {xp12_params}\n"
        print("New Spill:", new_spill_line)
        print("################### END SPILL-LIGHT ################")
        return new_spill_line
    if needle in line:
        print("--------------------- LANDING-LIGHTS -----------------")
        print("Old landinglights:", line.replace("\n", "").split(" "))
        # try:
        #     [light_param, light_name, lat, long, height] = line.replace("\n", "").split(
        #         " "
        #     )
        # except ValueError as err:
        #     print(err)

        new_line = line.replace(needle, new_landing_lights).replace("\n", "")
        new_line += f" {xp12_params}\n"
        print("New landinglights:", new_line)
        print("------------------------------------------------------")
        return new_line
    return line


def get_object_files(filepath):
    """Get all object files within filepath

    Args:
        filepath (str): Directory at wchich to start searching

    Returns:
        list: Of files
    """
    return list(Path(filepath).rglob("*.[oO][bB][jJ]"))


def create_new_object_file(file):
    """Create new aircraft obj file with X-Plane 12 light params

    Args:
        file (filepath): the eexisting aircraft object file
    """
    new_file = file.with_suffix(NEW_FILE_EXTENSION)

    if new_file.exists():
        new_file.unlink()

    with open(file) as obj_file:
        aircraft_type = str(file.parents[0]).split("/")[-1]
        xp12_params = determine_light_params(aircraft_type)

        for line in obj_file:
            with open(new_file, "a") as new_obj_file:
                newline = process_line(line, xp12_params)
                new_obj_file.write(newline)


def main():
    for file in get_object_files(filepath):
        make_backup(file)
        create_new_object_file(file)


if __name__ == "__main__":
    main()
