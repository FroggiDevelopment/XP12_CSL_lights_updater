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
from typing import TypedDict

from decorators.time_benchmark import time_benchmark

from .helpers import get_list_of_files
from .helpers import filepath_is_valid

from .custom_exceptions import NoFilesFoundError

log = logging.getLogger("aircraft_helpers")


class Aircraftobject(TypedDict):
    icao_type: str
    full_object_path: Path


def get_aircraft_icao_type(data_aircraft_description: str) -> str:
    """Gets the type of aircraft in ICAO format

    Args:
        data_aircraft_description (str): aircraft_description of data regarding the aircraft

    Returns:
        str: ICAO designator of the aircraft
    """

    aircraft_icao_type: str = ""
    _type_designator_definitions: set[str] = {
        "MATCHES",
        "ICAO",
        "AIRLINE",
        "LIVERY",
    }
    for line in data_aircraft_description.split("\n"):
        if any(
            type_designator in line for type_designator in _type_designator_definitions
        ):
            aircraft_icao_type = line.split()[1]
        else:
            continue
    return aircraft_icao_type

def get_aircraft_object_filepath(aircraft_description: str) -> str | None:
    """Create the filepath of the aircraft object from the given definition

    Args:
        aircraft_definition (str): aircraft definition
    Raises:
        FileNotFoundError: Raised if the file is not found with at the created path

    Returns:
        Path: Path to file if file exists.
        None: If no path could be created
    """
    for line_num, line in enumerate(aircraft_description.split("\n"), start=1):
        xsb_data = line.split()
        if len(xsb_data) > 0:
            # Get Path from OBJ8 Param. First part "must" be the package name, so it can be ignored.
            # The rest is a relative path starting from the location of the xsb_aircraft textfile.
            if xsb_data[0] != "OBJ8":
                continue
            else:
                # Check if line contains separator. If this is missing, the path can not be created!
                if not any(
                    (_separator := delimiter) in line
                    for delimiter in [":", "/"]
                ):
                    log.error(
                        f"Could not find separator in {line} at line -> {line_num}! Can not create path to object file!"
                    )
                    continue
                
                path_info = xsb_data[3]
                
                # Check if data contains possible objects with no lights. If so skip it.
                unwanted_objects = ["prop", "fan"]
                if any (unwanted_object in path_info for unwanted_object in unwanted_objects):
                    # log.error("Object is likely not an object with lights. Skipping this one!")
                    continue

                return path_info.split(_separator, 1)[1]
    return None

@time_benchmark
def get_aircraft_objects_from_xsb_file(searchpath: str) -> list[Aircraftobject]:
    """Get the aircraft objects from the xsb file and return the paths as a list.

    Args:
        searchpath (str): Topdirectory from which to search for the xsb_aircraft.txt file

    Returns:
        list[str]: List of paths to the aircraft objects in the searchpath.
    """

    xsb_files: list[Path]

    if Path(searchpath).is_dir() is False:
        log.error(f"Path {searchpath} is not a reachable directory!")
        raise FileNotFoundError(f"Path {searchpath} is not a reachable directory")

    try:
        xsb_files: list[Path] = get_list_of_files(searchpath, "xsb_aircraft.txt")
    except NoFilesFoundError as errormsg:
        log.error(errormsg)
        log.error("Please verify that your path is correct!")
        sys.exit()

    aircraft_object_files: list[Aircraftobject] = []

    log.info("Gathering all the aircraft objects.")
    # Start the search for the aircraft objects in the xsb_aircraft.txt file
    log.info(
        "Starting to collect files. This can take a while depending on your system and diskspeed."
    )
    for xsb_file in xsb_files:
        parentdir: Path = xsb_file.parent.absolute()

        try:
            with open(xsb_file, "r") as xsb_aircraft_file:
                content: str = xsb_aircraft_file.read()
                aircraft_descriptions = re.findall(
                    r"(?s)OBJ8_AIRCRAFT.*?(?=OBJ8_AIRCRAFT|$)",
                    content,
                )

                log.debug(
                    f"Aircrafts to convert in {str(parentdir)}: {len(aircraft_descriptions)}"
                )

                for aircraft_description in aircraft_descriptions:

                    aircraft_object: Aircraftobject = {
                        "icao_type": "",
                        "full_object_path": Path("Dummy"),
                    }
                    
                    aircraft_object["icao_type"] = get_aircraft_icao_type(aircraft_description)
                    aircraft_object_relative_path = get_aircraft_object_filepath(aircraft_description)
                    
                    if aircraft_object_relative_path is None:
                        log.error("No object path could be specified. Skipping this one!")
                        continue

                    aircraft_object["full_object_path"] = Path(parentdir, aircraft_object_relative_path)
                
                    if filepath_is_valid(aircraft_object["full_object_path"]) == True:
                        if not any(
                            entry.get("full_object_path")
                            == Path(aircraft_object["full_object_path"])
                            for entry in aircraft_object_files
                        ):
                            aircraft_object_files.append(aircraft_object)
                    else:
                        log.error(f"Filepath {aircraft_object['full_object_path']} is not valid. Missing file? Skipping this one!")
                        continue
        except FileNotFoundError as notfound:
            log.error(f"{xsb_file.name} not found! Skipping this one!", notfound)

    return aircraft_object_files


def is_lights_upgrade_already_done(item: str) -> bool:
    """Check if the conversion already is done

    Args:
        item (str): Textblock with the lights part

    Returns:
        bool: True if already done, False otherwise
    """
    already_updated: list[str] = re.findall("libxplanemp/controls/gear_ratio", item)
    if already_updated != []:
        log.debug("Taxilights already updated")
        return True
    return False


def fix_taxilights(item: str, extra_hide_anim: str) -> str:
    """Fixes the wrong dataref for taxilights where applicable

    Args:
        item (str): Textblock with the lights
        extra_hide_anim (str): String with the hide 'animation' to kill the lights when retracted.

    Returns:
        str : Fixed textblock
    """
    if is_lights_upgrade_already_done(item) is True:
        return item

    new_item = item.replace("landing_lites_on", "taxi_lites_on")
    original_taxi_anim_hide: list[str] = re.findall(
        "ANIM_hide.+taxi_lites_on", new_item
    )
    if original_taxi_anim_hide != []:
        new_item = new_item.replace(
            original_taxi_anim_hide[0],
            f"{original_taxi_anim_hide[0]}\n{extra_hide_anim}",
        )
    original_taxi_anim_show = re.findall("ANIM_show.+taxi_lites_on", new_item)
    if original_taxi_anim_show != []:
        new_item = new_item.replace(
            f"{original_taxi_anim_show[0]}\n",
            "",
        )
    return new_item


def fix_frontgear_landinglights(item: str, extra_hide_anim: str) -> str | None:
    """Fixes the case where the frontgear landinglights were still visibel after the landing gear is retracted

    Args:
        item (str): Textblock with the lights
        extra_hide_anim (str): String with the hide 'animation' to kill the lights when retracted.

    Returns:
        str | None: Fixed textblock, None if nothing has changed
    """
    if is_lights_upgrade_already_done(item) is True:
        return item

    get_original_landinglight_anim_hide: list[str] = re.findall(
        "ANIM_hide.+landing_lites_on", item
    )
    if get_original_landinglight_anim_hide == []:
        return None
    landing_lights_anim_hide = get_original_landinglight_anim_hide[0]
    light_parameter: list[str] = re.findall("LIGHT_PARAM airplane_landing.+", item)
    if light_parameter == []:
        return None
    x_position = float(light_parameter[0].split()[2])
    new_item = item
    if x_position < 0.5 and x_position > -0.5:
        new_item = item.replace(
            landing_lights_anim_hide,
            f"{landing_lights_anim_hide}\n{extra_hide_anim}",
        )
        get_original_landinglights_anim_show: list[str] = re.findall(
            "ANIM_show.+landing_lites_on", new_item
        )
        if get_original_landinglights_anim_show != []:
            new_item = new_item.replace(
                f"{get_original_landinglights_anim_show[0]}\n", ""
            )
    return new_item


def fix_lights_anomalies(object_content: str) -> str:
    """Fixes two things.
       Missing taxilight on some airplanes.
       The original dataref for the taxilights is set to landing_lites_on instead of taxi_lites_on.
       Landing lights on front gear were visible even if that gear is retracted.
       ANIM_hide animation is added to the front gear landing lights.

    Args:
        object_content (str): Original aricraft object content.

    Returns:
        object_content (str): Fixed aircraft object content.
    """
    result: list[str] = re.findall(
        "(?s)(?=ANIM_hide|ANIM_show)(.+?)(?=ANIM_end)", object_content
    )
    for item in result:
        extra_anim_hide: str = (
            "ANIM_hide -1.000000 0.500000 libxplanemp/controls/gear_ratio"
        )
        if "airplane_taxi_pm" in item:
            new_item = fix_taxilights(item, extra_anim_hide)
            object_content = object_content.replace(item, new_item)
        if "landing_lites" in item:
            new_item = fix_frontgear_landinglights(item, extra_anim_hide)
            if new_item == None or new_item == item:
                continue
            object_content = object_content.replace(item, new_item)

    return object_content
