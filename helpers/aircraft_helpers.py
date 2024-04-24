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
        xsb_files = get_list_of_files(searchpath, "xsb_aircraft.txt")
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
                    if any(
                        trigger in line.lower()
                        for trigger in [
                            "light.",
                            "cars",
                            "fan",
                            "prop",
                            "glass",
                            "rotor",
                            "engine",
                            "gear",
                        ]
                    ):
                        continue

                    if not line.startswith(
                        "OBJ8 "
                    ):  # Exclude the lines which have no light params
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
                        relative_path, object_name = aircraft_file_path_info.split(
                            _separator
                        )
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
    start_delimiter: str = (
        "ANIM_show 0.500000 2.000000 libxplanemp/controls/landing_lites_on"
    )
    end_delimiter: str = "ANIM_end"
    result = re.findall(
        f"(?s)({start_delimiter})(.+?)({end_delimiter})", object_content
    )

    string_from_tuple: str = ""

    # TODO: Add check if processing is necessary, else return original content
    for item in result:
        if any("airplane_taxi" in value for value in item):
            for row in item:
                string_from_tuple += row

        string_with_new_dataref = string_from_tuple.replace(
            "landing_lites_on", "taxi_lites_on"
        )
        new_object_content = object_content.replace(
            string_from_tuple, string_with_new_dataref
        )
        return new_object_content
    return object_content
