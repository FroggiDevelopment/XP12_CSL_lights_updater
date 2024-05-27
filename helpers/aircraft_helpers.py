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
                    # TODO: Better way to get the aircraft type??
                    # if line.startswith("EXPORT_NAME"):
                    #     print(f"This is the package name: {line.split()[1]}")
                    #     sys.exit()
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

                    # Get Path from OBJ8 Param. First part "must" be the package name, so it can be ignored.
                    # The rest is a relative path starting from the location of the xsb_aircraft textfile.
                    aircraft_object_path = Path(
                        aircraft_file_path_info.split(_separator, 1)[1]
                    )
                    # Create the full path
                    full_object_path = Path(parentdir, aircraft_object_path)

                    if full_object_path.exists() is False:
                        log.error(f"File {full_object_path} does not exist! Skipping!")
                        continue

                    if full_object_path not in aircraft_object_files:
                        aircraft_object_files.append(full_object_path)

        except FileNotFoundError as notfound:
            log.error(f"{xsb_file.name} not found! Skipping these!", notfound)

    return aircraft_object_files


def is_lights_upgrade_already_done(item: str) -> bool:
    already_updated: list[str] = re.findall("libxplanemp/controls/gear_ratio", item)
    if already_updated != []:
        log.debug("Taxilights already updated")
        return True
    return False


def fix_taxilights(item: str, extra_hide_anim: str) -> str:
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
        object_content (str): Fixed aricraft object content.
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
