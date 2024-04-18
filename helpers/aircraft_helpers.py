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

    # Separator differ between Bluebell and X-CSL, standard is / in this case.
    _separator: str = "/"

    # Start the search for the aircraft objects in the xsb_aircraft.txt file
    for xsb_file in xsb_files:
        parentdir: Path = xsb_file.parent.absolute()

        try:
            with open(xsb_file, "r") as xsb_aircraft_file:
                for line in xsb_aircraft_file:
                    # Some 'specials' in xsb_aircraft.txt files to ignore
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

                    if not line.startswith("OBJ8 "):  # Exclude the lines which have no light params
                        continue
                    list_of_params: list[str] = line.split(" ")
                    aircraft_dir_file_info: str = list_of_params[3]
                    number_of_path_params: int = 0

                    if any(
                        (_separator := delimiter) in aircraft_dir_file_info
                        for delimiter in [":", "/"]
                    ):
                        pass
                    else:
                        log.warning(
                            f"Could not find separator in {aircraft_dir_file_info}! No path to object creatable!"
                        )
                        sys.exit()

                    number_of_path_params = len(
                        aircraft_dir_file_info.split(_separator)
                    )
                    if number_of_path_params == 3:
                        _, relative_path, object_name = aircraft_dir_file_info.split(_separator)
                    elif number_of_path_params == 2:
                        relative_path, object_name = aircraft_dir_file_info.split(_separator)
                    else:
                        log.warning(
                            f"Found not enough path parameters in {aircraft_dir_file_info}! xsb_aircraft.txt file is not valid!"
                        )
                        sys.exit()

                    object_path = Path(parentdir, relative_path, object_name.rstrip("\n"))

                    if object_path.exists() is False:
                        log.error(f"File {object_path} does not exist! Skipping!")
                        object_path = None

                    if (
                        object_path is not None
                        and object_path not in aircraft_object_files
                    ):
                        aircraft_object_files.append(object_path)
        except FileNotFoundError as notfound:
            log.error(f"{xsb_file.name} not found! Skipping these!", notfound)
    return aircraft_object_files
