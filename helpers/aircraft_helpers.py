"""
Copyright (C) 2025  Richard J.M. Muller / Froggi

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

import re
import logging
import logging.config
from pathlib import Path

from decorators.time_benchmark import time_benchmark

from .helpers import get_list_of_files
from .helpers import paused_exit
from .init_logging import init_logging

from .custom_exceptions import NoFilesFoundError

# Setup logging
init_logging()
log = logging.getLogger(__name__)

IGNORE_OBJECTS: list[str] = ["glass", "prop",
                             "Contrail", "fan", "rotor", "car", "BLUR"]
ICAO_IDENTIFIERS: list[str] = [
    "MATCHES",
    "ICAO",
    "AIRLINE",
    "LIVERY"]


def get_path_to_aircraft_object(line: str) -> str:
    """Extracts the path to the aircraft object from the line

    Args:
        line (str): line with xsb aircaft data

    Returns:
        str: string representation of the path
    """
    if not any((_separator := delimiter) in line for delimiter in [":", "/"]):
        log.error(
            f"Could not find separator in {line} Can not create path to object file!")
        return "no sep error"
    else:
        pathinfo: str = line.split()[3]
        # get rid of packagename, as this is ALWAYS the first part of the pathinfo!
        path_only: str = pathinfo.split(_separator, 1)[1]
        return (path_only)


@time_benchmark
def get_aircraft_objects_from_xsb_file(searchpath: Path) -> list[dict[str, str]]:
    """Get the aircraft objects from the xsb file and return the paths as a list.

    Args:
        searchpath (str): Topdirectory from which to search for the xsb_aircraft.txt file

    Returns:
        list[dict[str, str]]: List of dictionaries with path and object dat of aircrafts.
    """
    # TODO: Review this bunch of code :-) Maybe it can be improved.
    xsb_files: list[Path] = []

    if not searchpath.is_dir():
        log.error(
            f"Path {str(searchpath)} is not a reachable directory! Please review your specified path!")
        paused_exit()

    try:
        xsb_files: list[Path] = get_list_of_files(
            searchpath, "xsb_aircraft.txt")
    except NoFilesFoundError as errormsg:
        log.error(errormsg)
        log.error("Please verify that your path is correct!")
        paused_exit()

    aircraft_object_files: list[dict[str, str]] = []
    unique_aircraft_objects: list[dict[str, str]] = []

    log.info("Gathering all the aircraft objects.")
    # Start the search for the aircraft objects in the xsb_aircraft.txt file
    log.info(
        "Starting to collect files. This can take a while depending on your system and diskspeed."
    )

    for xsb_file in xsb_files:
        parentdir: str = str(xsb_file.parent.absolute())
        with open(xsb_file, "r") as xsb_aircraft_file:
            content: str = xsb_aircraft_file.read()
            aircraft_descriptions: list[str] = re.findall(
                r"(?s)OBJ8_AIRCRAFT.*?(?=OBJ8_AIRCRAFT|$)",
                content,
            )

            for aircraft_description in aircraft_descriptions:
                aircraft_object: dict[str, str] = {}
                legit_object_paths: list[str] = []

                for line in aircraft_description.split("\n"):
                    # Get ICAO identifier for this aircraft
                    if line.startswith("#"):
                        continue
                    if (any(iaco_identifier in line for iaco_identifier in ICAO_IDENTIFIERS) and
                            not line.startswith("#")):
                        icao = line.split()[1]
                        if icao in aircraft_object:
                            log.debug(f"ICAO {icao} is already set!")
                            continue
                        else:
                            aircraft_object["icao_type"] = icao

                    # Ignore lines with no usefull information
                    if not line.startswith("OBJ8 "):
                        continue
                    if any(ignore_object in line for ignore_object in IGNORE_OBJECTS):
                        continue

                    # Get the path to this aircraft object
                    path = get_path_to_aircraft_object(line)
                    full_path = parentdir + "/" + path
                    if not Path(full_path).exists():
                        log.debug(
                            f"File {full_path} does not exist! Windows mentality? :-) Trying with lowercase extension.")
                        path = path.replace(".OBJ", ".obj")
                        full_path = parentdir + "/" + path
                        if not Path(full_path).exists():
                            log.error(
                                f"File {full_path} does not exist either! Giving up on this one.")
                            continue
                        log.debug(f"Path {full_path} seems ok.")

                    legit_object_paths.append(full_path)
                if aircraft_object != {} and len(legit_object_paths) > 0:
                    for legit_object_path in legit_object_paths:
                        temp_object = aircraft_object.copy()
                        temp_object["full_object_path"] = legit_object_path
                        aircraft_object_files.append(temp_object)

        [unique_aircraft_objects.append(
            val) for val in aircraft_object_files if val not in unique_aircraft_objects]
    return unique_aircraft_objects
