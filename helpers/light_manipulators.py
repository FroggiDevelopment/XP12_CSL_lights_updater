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
from .init_logging import init_logging

# Some constants
POSITION_IDENTIFIERS = ["_left", "_right", "_tail"]
LIGHTS_TO_IGNORE = [
    "headlight",
    "_size",
    "_sp",
    "taillight",
    "_core",
    "_size",
    "_omni",
    "_dir",
    "airplane_strobe_omni",
    "airplane_beacon_",
    "full_custom_halo_night",
    "_glow",
    "_flare",
    "logo",
    "PLN_",
    "_core",
    "_flare",
    "_glow",
    "LIGHT_SPILL_CUSTOM",
]

# Setup logging
init_logging()
log = logging.getLogger(__name__)

def filter_unwanted_light_params(line: str) -> str:
    """Filter out light params that are old or otherwise wrong.
       Can be expanded for future cases.

    Args:
        line (str): Line with light parameters

    Returns:
        str: Corrected line with light parameters
    """
    # Make a more readable line for output
    output_line = re.sub(r'\s+',' ', line)
    
    # If light is on the ignore list, ignore it and retrun empty line
    if any(to_ignore in line for to_ignore in LIGHTS_TO_IGNORE):
        return ""
    
    # Check if old LIGHT_NAMED param exists and replace it with the new one
    if "LIGHT_NAMED" in line:
        log.debug(f"Replacing LIGHT_NAMED in line {output_line} to LIGHT_PARAM")
        line = line.replace("LIGHT_NAMED", "LIGHT_PARAM")
    
    # Some lines are commented out... Must be undone
    if "#LIGHT_PARAM" in line or "#LIGHT_NAMED" in line:
        log.debug(f"Removing leading # from line {output_line}")
        line = line.replace("#LIGHT_PARAM", "LIGHT_PARAM")      

    # Remove positional name from line
    if any(position in line for position in POSITION_IDENTIFIERS):
        for item in POSITION_IDENTIFIERS:
            line = line.replace(item, "")

    return line

def is_front_gear_fix_done(item: str) -> bool:
    """Check if the conversion already is done

    Args:
        item (str): Textblock with the lights part

    Returns:
        bool: True if already done, False otherwise
    """
    already_updated: list[str] = re.findall("libxplanemp/controls/gear_ratio", item)
    if already_updated == []:
        return False
    return True


def fix_taxilights(item: str, extra_hide_anim: str) -> str:
    """Fixes the wrong dataref for taxilights where applicable

    Args:
        item (str): Textblock with the lights
        extra_hide_anim (str): String with the hide 'animation' to kill the lights when retracted.

    Returns:
        str : Fixed textblock
    """
    log.debug("Fixing frontgear taxilights hide animation.")
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


def fix_frontgear_landinglights(item: str, extra_hide_anim: str) -> str:
    """Fixes the case where the frontgear landinglights were still visibel after the landing gear is retracted

    Args:
        item (str): Textblock with the lights
        extra_hide_anim (str): String with the hide 'animation' to kill the lights when retracted.

    Returns:
        str | None: Fixed textblock, None if nothing has changed
    """
    log.debug("Fixing frontgear landinglights hide animation.")
    get_original_landinglight_anim_hide: list[str] = re.findall(
        "ANIM_hide.+landing_lites_on", item
    )
    if get_original_landinglight_anim_hide == []:
        return item
    landing_lights_anim_hide = get_original_landinglight_anim_hide[0]
    light_parameter: list[str] = re.findall("LIGHT_PARAM airplane_landing.+", item)
    if light_parameter == []:
        return item
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
    animations: list[str] = re.findall(
        "(?s)(?=ANIM_hide|ANIM_show)(.+?)(?=ANIM_end)", object_content
    )
    for animation in animations:
        if is_front_gear_fix_done(animation):
            log.debug("Front gear taxilights already fixed.")
            continue
        extra_anim_hide: str = (
            "ANIM_hide -1.000000 0.500000 libxplanemp/controls/gear_ratio"
        )
        if "airplane_taxi_pm" in animation:
            new_animation = fix_taxilights(animation, extra_anim_hide)
            object_content = object_content.replace(animation, new_animation)
        if "landing_lites" in animation:
            new_animation = fix_frontgear_landinglights(animation, extra_anim_hide)
            if new_animation == animation:
                continue
            object_content = object_content.replace(animation, new_animation)

    return object_content

def add_lateral_position_to_lights(line: str) -> str:
    """To determine directional parameters add left, right or tail to the light param
       based on x-y-position of the light.
       Will be removed again later on in the process.

    Args:
        line (str): Line with light-parameters.

    Returns:
        str: Line with 'positional' light-name-parameters. I.e. airplane_nav_rigt
    """
    # If the line already includes position, return it unprocessed.
    if any(position in line for position in POSITION_IDENTIFIERS):
        return line

    _x_position = float(line.split()[2:3][0])
    actual_lighttype = line.split()[1]

    if (_x_position) > -0.50 and _x_position < 0.50:
        lighttype = f"{actual_lighttype}_tail"
    elif (_x_position) < -0.50:
        lighttype = f"{actual_lighttype}_left"
    else:
        lighttype = f"{actual_lighttype}_right"

    return line.replace(actual_lighttype, lighttype)