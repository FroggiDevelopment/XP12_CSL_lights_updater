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
# from typing import TypedDict

from decorators.time_benchmark import time_benchmark

from .helpers import get_list_of_files
# from .helpers import filepath_is_valid

from .custom_exceptions import NoFilesFoundError

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.propagate = False

# Add screen handler
screen = logging.StreamHandler()
screen.setLevel(logging.INFO)
screenformatter = logging.Formatter("%(name)-12s: %(levelname)-8s - %(message)s")
screen.setFormatter(screenformatter)

# Add file handler
file_handler = logging.FileHandler("lights_updater.log", mode="w")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter("%(name)-12s: %(levelname)-8s - (%(asctime)s) at line: %(lineno)d [%(filename)s] %(message)s")
file_handler.setFormatter(file_formatter)

log.addHandler(screen)
log.addHandler(file_handler)

IGNORE_OBJECTS: list[str] = ["glass", "prop", "Contrail", "fan", "rotor", "car", "BLUR"]
ICAO_IDENTIFIERS: list[str] = [
    "MATCHES",
    "ICAO",
    "AIRLINE",
    "LIVERY"]

# class Aircraftobject(TypedDict):
#     icao_type: str
#     full_object_path: Path


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

def get_path_to_aircraft_object(line: str) -> str:
    """Extracts the path to the aircraft object from the line

    Args:
        line (str): line with xsb aircaft data

    Returns:
        str: string representation of the path
    """
    if not any((_separator := delimiter) in line for delimiter in [":", "/"]):
        log.error(f"Could not find separator in {line} Can not create path to object file!")
        return "no sep error"
    else:
        pathinfo: str = line.split()[3]
        # get rid of packagename, as this is ALWAYS the first part of the pathinfo!
        path_only: str = pathinfo.split(_separator, 1)[1]
        return(path_only)
    
@time_benchmark
def get_aircraft_objects_from_xsb_file(searchpath: str) -> list[dict[str, str]]:
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
                
                for line in aircraft_description.split("\n"):
                    # Get ICAO identifier for this aircraft
                    if line.startswith("#"):
                        continue
                    if any (iaco_identifier in line for iaco_identifier in ICAO_IDENTIFIERS) and not line.startswith("#"):
                        icao = line.split()[1]
                        if icao in aircraft_object:
                            log.debug(f"ICAO {icao} is already set!")
                            continue
                        else:
                            aircraft_object["icao_type"] = icao
                            
                    # Ignore lines with no usefull information
                    if not line.startswith("OBJ8 "):
                        continue
                    if any (ignore_object in line for ignore_object in IGNORE_OBJECTS):
                        continue
                    
                    #Get the path to this aircraft object
                    path = get_path_to_aircraft_object(line)
                    full_path = parentdir + "/" + path
                    aircraft_object["full_object_path"] = full_path
                if aircraft_object != {}:    
                    aircraft_object_files.append(aircraft_object)
    
        [unique_aircraft_objects.append(val) for val in aircraft_object_files if val not in unique_aircraft_objects]
    return unique_aircraft_objects

#TODO: Can this be handled with strings? Has impact on lights_updater.py!
def create_file_list_from_aircraft_objects(aircraft_objects: list[dict[str,str]]) -> list[Path]:
    aircraft_files: list[Path] = []
    for aircraft_object in aircraft_objects:
        if Path(aircraft_object["full_object_path"]).exists():
            aircraft_files.append(Path(aircraft_object["full_object_path"]))
    return aircraft_files

def is_lights_upgrade_already_done(item: str) -> bool:
    """Check if the conversion already is done

    Args:
        item (str): Textblock with the lights part

    Returns:
        bool: True if already done, False otherwise
    """
    already_updated: list[str] = re.findall("libxplanemp/controls/gear_ratio", item)
    if already_updated == []:
        return False
    log.debug("Taxilights already updated")
    return True


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
