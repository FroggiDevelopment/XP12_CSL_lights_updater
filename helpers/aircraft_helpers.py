"""
Copyright (C) 2024  Richard J.M. Muller / Froggi

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>
"""

import sys
import re
import logging
from pathlib import Path

from .helpers import get_list_of_files

# from .helpers import tuple_to_string
from .custom_exceptions import NoFilesFoundError

log = logging.getLogger("aircraft_helpers")


def get_aircraft_objects_from_xsb_file(searchpath: str) -> list[Path]:
    """Get the aircraft objects from the xsb file and return the paths as a list.

    Args:
        searchpath (str): Topdirectory from which to search for the xsb_aircraft.txt file

    Returns:
        list[str]: List of paths to the aircraft objects in the searchpath.
    """
    if Path(searchpath).is_dir() is False:
        log.error(f"Path {searchpath} is not a reachable directory!")
        raise FileNotFoundError(f"Path {searchpath} is not a reachable directory")

    try:
        xsb_files: list[Path] = get_list_of_files(searchpath, "xsb_aircraft.txt")
    except NoFilesFoundError as errormsg:
        log.error(errormsg)
        log.error("Please verify that your path is correct!")
        sys.exit()

    aircraft_object_files: list[Path] = []

    # Start the search for the aircraft objects in the xsb_aircraft.txt file
    for xsb_file in xsb_files:
        parentdir: Path = xsb_file.parent.absolute()

        try:
            with open(xsb_file, "r") as xsb_aircraft_file:
                for line_num, line in enumerate(xsb_aircraft_file, start=1):
                    # As some CSL aircraft are made with more then one object, also not recommended,
                    # some of those in xsb_aircraft.txt files have to be ignored!
                    # if any(
                    #     trigger in line.lower()
                    #     for trigger in [
                    #         "light.",
                    #         "cars",
                    #         "fan",
                    #         "prop",
                    #         "glass",
                    #         "rotor",
                    #         "engine",
                    #         "gear",
                    #     ]
                    # ):
                    #     continue

                    if not line.startswith(
                        "OBJ8 "
                    ):  # Exclude lines with no aircraft object info
                        continue

                    aircraft_file_path_info: str = line.split()[3]

                    if any(
                        (_separator := delimiter) in aircraft_file_path_info
                        for delimiter in [":", "/"]
                    ):
                        pass
                    else:
                        log.error(
                            f"Could not find separator in {aircraft_file_path_info} at line -> {line_num}! No path to object creatable!"
                        )
                        continue

                    number_of_path_params = len(
                        aircraft_file_path_info.split(_separator)
                    )
                    if number_of_path_params == 3:
                        _, relative_path, object_name = aircraft_file_path_info.split(
                            _separator
                        )
                    elif number_of_path_params == 2:
                        _, object_name = aircraft_file_path_info.split(_separator)
                        relative_path = "."
                    else:
                        log.warning(
                            f"Found not enough path parameters in {aircraft_file_path_info}! xsb_aircraft.txt file is not valid!"
                        )
                        sys.exit()

                    object_path = Path(
                        parentdir, relative_path, object_name.rstrip("\n")
                    )

                    if object_path.exists() is False:
                        log.error(f"File {object_path} does not exist! Skipping!")
                        continue

                    if object_path not in aircraft_object_files:
                        aircraft_object_files.append(object_path)

        except FileNotFoundError as notfound:
            log.error(f"{xsb_file.name} not found! Skipping these!", notfound)
    return aircraft_object_files


def fix_taxilights_dataref(object_content: str) -> str:
    """Fixes the wrong dataref for taxilights.
       The original dataref for the taxilights is set to landing_lites_on instead of taxi_lites_on.
       Gets corrected so the taxilights are visible.

    Args:
        object_content (str): Original aricraft object content.

    Returns:
        str: Fixed aricraft object content.
    """
    # start_delimiter: str = (
    #     "ANIM_show|ANIM_hide.*libxplanemp/controls/landing_lites_on?$"
    # )
    # end_delimiter: str = "ANIM_end"
    # result: list[tuple[str, str, str]] = re.findall(
    #     f"(?s)({start_delimiter})(.+?)({end_delimiter})", object_content
    # )
    result: list[str] = re.findall("(?s)(?=ANIM_hide)(.+?)(?=ANIM_end)", object_content)
    for item in result:
        if "airplane_taxi_pm" in item:
            item = item.replace("landing_lites_on", "taxi_lites_on")
        if "landing_lites" in item:
            anim_hide: str = (
                "ANIM_hide -1.000000 0.000000 libxplanemp/controls/gear_ratio"
            )
            # print(f"Light #{index}\n{item}")
            to_replace: list[str] = re.findall("^ANIM_hide.+landing_lites_on", item)
            print(type(to_replace[0]))
            print(item.replace(to_replace[0], f"{to_replace[0]}\n{anim_hide}"))
            light_parameter: list[str] = re.findall(
                "LIGHT_PARAM airplane_landing.+", item
            )
            x_position = float(light_parameter[0].split()[2])
            if x_position < 0.5 and x_position > -0.5:
                print(
                    item.replace(
                        "libxplanemp/controls/landing_lites_on",
                        f"libxplanemp/controls/landing_lites_on\n{anim_hide}",
                    )
                )

    sys.exit()
    # TODO: Add check if processing is necessary, else return original content
    # TODO: Add fix for landing lights on retracted landing gear
    new_object_content: str = ""
    for item in result:
        (_, lights, __) = item
        if any("airplane_taxi" in value for value in item):
            fixed_taxilights_dataref = fix_taxilights(lights)
            new_object_content = object_content.replace(
                lights, fixed_taxilights_dataref
            )
        if any("airplane_landing_pm" in value for value in item):
            fixed_front_landing_lights = add_hide_option_to_front_landing_lights(item)
            if fixed_front_landing_lights is not None:
                if new_object_content != "":
                    new_object_content = new_object_content.replace(
                        lights, fixed_front_landing_lights
                    )
                else:
                    new_object_content = object_content.replace(
                        lights, fixed_front_landing_lights
                    )
    return new_object_content


def fix_taxilights(taxilights_string: str) -> str:
    string_with_new_dataref: str = ""
    for row in taxilights_string.split("\n"):
        if "landing_lites_on" not in row:
            continue
        string_with_new_dataref = taxilights_string.replace(
            "landing_lites_on", "taxi_lites_on"
        )

    return string_with_new_dataref


def add_hide_option_to_front_landing_lights(item: tuple[str, str, str]) -> str | None:
    anim_hide: str = "ANIM_hide -1.000000 0.000000 libxplanemp/controls/gear_ratio"

    (_, lightdefinition_strings, __) = item
    param_to_replace: list[tuple[str, str, str]] = re.findall(
        f"(?s)(ANIM_hide.*libxplanemp/controls/landing_lites_on)",
        lightdefinition_strings,
    )
    print("Does it match?", param_to_replace)

    for line in lightdefinition_strings.split("\n"):
        if "airplane_landing_pm" in line:
            x_position = float(line.split()[2])
            if x_position < 0.5 and x_position > -0.5:
                return lightdefinition_strings.replace(
                    "libxplanemp/controls/landing_lites_on",
                    f"libxplanemp/controls/landing_lites_on\n{anim_hide}",
                )
    return None
