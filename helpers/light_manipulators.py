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
import os
import re
import logging
import random
from .init_logging import init_logging
from .aircraft_light_params import get_aircraft_categories
# from .aircraft_light_params import get_light_params_for_aircraft_type

# Some constants
POSITION_IDENTIFIERS = ["_left", "_right", "_tail"]

LIGHTS_TO_IGNORE = [
    "headlight",
    "taillight",
    "airplane_strobe_sp_tail",
    "_flare",
    "_size",
    "airplane_strobe_omni",
    "airplane_beacon_rotate_",
    "full_custom_halo_night",
    "logo",
    "PLN_",
    "LIGHT_SPILL_CUSTOM",
]

# Setup logging
init_logging()
log = logging.getLogger(__name__)

aircraft_types = get_aircraft_categories()


def get_basic_light_params(line_with_light_information: str) -> str:
    """ Get basic light params

    Args:
        line_with_light_information (str): The line with the light information

    Returns:
        str: line with onlyspecifier, lighttype, x, y, z params
    """
    return " ".join(line_with_light_information.split()[0:5])


def get_leading_whitespaces(line_with_light_information: str) -> str:
    """ Get leading whitespaces from line to ensure identation is kept
        This is for the readability of the obj files themself

    Args:
        line_with_light_information (str): The line with the light information

    Returns:
        str: leading whitespaces
    """
    leading_whitespaces = re.match(r"^\s*", line_with_light_information)

    if leading_whitespaces is None:
        return ""
    return leading_whitespaces.group()


def create_spill_lines(line_with_light_information: str, light_type: str) -> str:
    """ Create spill line

    Args:
        line_with_light_information (str): The line with the light information

    Returns:
        str: line with spill identifier and params
    """
    spill_line = line_with_light_information.replace("_bb", "_pm")
    spill_line = reduce_spill_intensity(spill_line, light_type)
    return spill_line


def convert_airplane_landing_lights(animation: str, landing_light_params: str) -> str:
    """ Convert airplane landing lights

    Args:
        animation (str): The animations sequence with the landing lights

    Returns:
            str: The updated animations sequence with landing lights
        """
    print("Converting landing lights")
    if re.findall(r"LIGHT_PARAM.+airplane_landing", animation) == []:
        return animation

    for line in animation.splitlines():
        leading_whitespaces = get_leading_whitespaces(line)

        if "airplane_landing_" in line:
            animation = animation.replace(line, "")
            continue

        if "airplane_landing" in line:
            # Remove possible comment sign
            if "#" in line:
                new_line = line.replace("#", "")
            else:
                new_line = line
            new_line = new_line.replace(
                "airplane_landing", "airplane_landing_bb")
            just_light = get_basic_light_params(new_line)

            new_light_line = f"{leading_whitespaces}{just_light} {landing_light_params}"

            spill_line = create_spill_lines(new_light_line, "airplane_landing")

            animation = animation.replace(
                line, new_light_line + "\n" + leading_whitespaces + spill_line)

    new_animation = os.linesep.join(
        [line for line in animation.splitlines() if line])

    # Fix landing lights on frontgear
    if is_front_gear_fix_done is False:
        new_animation = fix_frontgear_landinglights(new_animation)

    return new_animation


def convert_airplane_taxi_lights(animation: str, taxi_light_params: str) -> str:
    print("Converting taxilights")

    for line in animation.splitlines():
        leading_whitespaces = get_leading_whitespaces(line)

        if "airplane_taxi_" in line:
            animation = animation.replace(line, "")
            continue

        # As there are rare cases of landing lights in these animations... fix it!
        if "airplane_landing" in line:
            line = line.replace("airplane_landing", "airplane_taxi")

        if "airplane_taxi" in line:
            # Remove possible comment sign
            if "#" in line:
                new_line = line.replace("#", "")
            else:
                new_line = line
            new_line = new_line.replace("airplane_taxi", "airplane_taxi_bb")
            just_light = get_basic_light_params(new_line)
            new_light_line = f"{leading_whitespaces}{just_light} {taxi_light_params}"
            spill_line = create_spill_lines(new_light_line, "airplane_taxi")
            animation = animation.replace(
                line, new_light_line + "\n" + leading_whitespaces + spill_line)

    new_animation = os.linesep.join(
        [line for line in animation.splitlines() if line])

    # Add ANIM_hide animation to hide when rectracted
    if is_front_gear_fix_done(new_animation) is False:
        new_animation = fix_taxilights(new_animation)
    return new_animation


def convert_airplane_nav_lights(animation: str, nav_light_params: str) -> str:
    print("Converting navlights")

    # light_params = get_light_params_for_aircraft_type(aircraft_icao_type)

    for line in animation.splitlines():
        leading_whitespaces = re.match(r"\s*", line)

        if leading_whitespaces is not None:
            leading_whitespaces = leading_whitespaces.group()

        OLD_NAVS = ["airplane_nav_right_",
                    "airplane_nav_left_", "airplane_nav_tail_", "_sp"]
        if any(old_navs in line for old_navs in OLD_NAVS):
            animation = animation.replace(line, "")
            continue
        if "airplane_nav" in line:
            print("NAVSSSSSS")
            # nav_light = line.split()[1]
            # Remove possible comment sign
            if "#" in line:
                new_line = line.replace("#", "")
            else:
                new_line = line

            just_light = get_basic_light_params(new_line)
            new_light_line = f"{leading_whitespaces}{just_light} {nav_light_params}"
            print(new_light_line)
            animation = animation.replace(line, new_light_line)

    new_animation = os.linesep.join(
        [line for line in animation.splitlines() if line])

    return new_animation


def convert_airplane_beacon_lights(animation: str, aircraft_icao_type: str) -> str:
    print("Converting beacon lights")
    return ("hello")


def convert_airplane_flashing_beacon_lights(animation: str, aircraft_icao_type: str) -> str:
    print("Converting beacon to flashing beacon light")
    return ("hello")


def convert_airplane_strobe_lights(animation: str, aircraft_icao_type: str) -> str:
    print("COnvetring strobe lights")
    return ("hello")


def increase_flashing_beacon_light_intensity(animation: str) -> str:
    """ Increase the candelar for the beacon if they are flashing

    Args:
        animation (str): The animations sequence with the beacons

    Returns:
            str: The updated animations sequence with increased candelar intensity for beacon lights
        """
    increase_beacon_intensity_factor: float = 2.0
    light_intensity_list: list[str] = re.findall(
        r"\d+cd", animation.lower())
    unique_light_intensity_list: list[str] = []
    [unique_light_intensity_list.append(
        val) for val in light_intensity_list if val not in unique_light_intensity_list]

    # Increase light intensity for flashing
    for light_intensity in unique_light_intensity_list:
        original_candelar = float(light_intensity.replace("cd", ""))
        increased_candelar = original_candelar * increase_beacon_intensity_factor
        new_light_intensity = f"{increased_candelar}cd"
        animation = animation.replace(
            light_intensity, new_light_intensity)
    return animation


def convert_beacons_to_flashing_beacons(animation: str, aircraft_icao_type: str) -> str:
    """ Converts existing beacon lights to flashing lights simulating a flashing beacon

    Args:
        animation (str): The original animations sequence from the aircraft object file
        aircraft_icao_type (str): ICAO identifier for this specific airrcaft to determine if conversion is neccessary.

    Returns:
        str: Converted animation with flashing 'beacon' lights and an increased intensity
    """

    flash_sequences = [
        "ANIM_show    0.0 0.1    sim/time/total_running_time_sec",
        "ANIM_show    0.3 0.4    sim/time/total_running_time_sec",
        "ANIM_show    0.6 0.7    sim/time/total_running_time_sec"
    ]
    flash_sequence = random.choice(flash_sequences)
    new_anim_hide = f"""
    ANIM_hide	-1.0 1.0	libxplanemp/controls/beacon_lites_on
    {flash_sequence}
    ANIM_keyframe_loop 1.5
    """
    # TODO: Is it better to use list of icao-identifiers??? How to determine who's in?
    aircraft_categories = get_aircraft_categories()

    for category in aircraft_categories.items():
        if aircraft_icao_type in category[1] and category[0] in ["medium", "high"]:
            original_beacon_anim_hide = re.findall(
                "ANIM_hide.+libxplanemp/controls/beacon_lites_on", animation)

            animation = animation.replace(
                original_beacon_anim_hide[0], new_anim_hide)

            animation = animation.replace(
                "airplane_beacon", "airplane_generic")
            log.debug(
                f"Converted beacon lights for {aircraft_icao_type} to flashing beacons.")
            animation = increase_flashing_beacon_light_intensity(animation)
    return animation


def filter_unwanted_light_params(line: str) -> str:
    """Filter out light params that are old or otherwise wrong.
       Can be expanded for future cases.

    Args:
        line (str): Line with light parameters

    Returns:
        str: Corrected line with light parameters
    """
    # Make a more readable line for output
    # output_line = re.sub(r'\s+', ' ', line)

    # If light is on the ignore list, ignore it and retrun empty line
    if any(to_ignore in line for to_ignore in LIGHTS_TO_IGNORE):
        return ""

    # Check if old LIGHT_NAMED param exists and replace it with the new one
    if "LIGHT_NAMED" in line:
        line = line.replace("LIGHT_NAMED", "LIGHT_PARAM")

    # Some lines are commented out... Must be undone
    if "#LIGHT_PARAM" in line:
        line = line.replace("#LIGHT_PARAM", "LIGHT_PARAM")

    return line


def is_front_gear_fix_done(animation: str) -> bool:
    """Check if adding the hide animation when gear is retracted already is done

    Args:
        animation (str): Textblock with the lights part

    Returns:
        bool: True if already done, False otherwise
    """
    already_updated: list[str] = re.findall(
        "libxplanemp/controls/gear_ratio", animation)
    if already_updated == []:
        return False
    return True


def fix_taxilights(animation: str) -> str:
    """Fixes the wrong dataref for taxilights where applicable

    Args:
        animation (str): Textblock with the lights
        extra_hide_anim (str): String with the hide 'animation' to kill the lights when retracted.

    Returns:
        str : Fixed textblock
    """
    log.debug("Fixing frontgear taxilights hide animation.")
    extra_anim_hide: str = (
        "ANIM_hide -1.000000 0.500000 libxplanemp/controls/gear_ratio"
    )
    new_animation = animation.replace("landing_lites_on", "taxi_lites_on")
    original_taxi_anim_hide: list[str] = re.findall(
        r"\s*ANIM_hide.+taxi_lites_on", new_animation
    )
    leading_whitespaces = get_leading_whitespaces(original_taxi_anim_hide[0])

    if original_taxi_anim_hide != []:
        new_animation = new_animation.replace(
            original_taxi_anim_hide[0],
            f"{original_taxi_anim_hide[0]}\n{leading_whitespaces}{extra_anim_hide}",
        )
    original_taxi_anim_show = re.findall(
        "ANIM_show.+taxi_lites_on", new_animation)

    if original_taxi_anim_show != []:
        new_animation = new_animation.replace(
            f"{original_taxi_anim_show[0]}\n",
            "",
        )
    return new_animation


def correct_wrong_landing_lights_in_taxi_lights_animation(animation: str):
    taxilight_animations = re.findall(
        r"(?s)(?=ANIM_show\s+1\s+1\s+libxplanemp/controls/taxi_lites_on)(.+?)(?=ANIM_end)", animation)

    if len(taxilight_animations) > 0:
        for taxilight_animation in taxilight_animations:
            new_taxilight_animation = ""
            if "airplane_landing" in taxilight_animation:
                new_taxilight_animation = taxilight_animation.replace(
                    "airplane_landing", "airplane_taxi")
                log.debug(
                    "Repaired wrong lighttype from landing to taxi!")
            if new_taxilight_animation != "":
                animation = animation.replace(
                    taxilight_animation, new_taxilight_animation)
    return animation


def fix_frontgear_landinglights(animation: str) -> str:
    """Fixes the case where the frontgear landinglights were still visible after the landing gear is retracted

    Args:
        animation (str): Textblock with the lights
        extra_hide_anim (str): String with the hide 'animation' to kill the lights when retracted.

    Returns:
        str | None: Fixed textblock, None if nothing has changed
    """
    log.debug("Fixing frontgear landinglights hide animation.")

    extra_anim_hide: str = (
        "ANIM_hide -1.000000 0.500000 libxplanemp/controls/gear_ratio"
    )

    original_landinglight_anim_hide: list[str] = re.findall(
        r"\s*ANIM_hide.+libxplanemp/controls/landing_lites_on", animation
    )

    original_landinglights_anim_show: list[str] = re.findall(
        r"^\s*ANIM_show.+landing_lites_on", animation
    )

    if original_landinglight_anim_hide == []:
        log.debug("Nothing found")
        return animation
    landing_lights_anim_hide = original_landinglight_anim_hide[0]
    leading_whitespaces = get_leading_whitespaces(
        landing_lights_anim_hide).replace("\n", "")

    light_parameter: list[str] = re.findall(
        "LIGHT_PARAM airplane_landing.+", animation)

    x_position = float(light_parameter[0].split()[2])

    if x_position < 0.5 and x_position > -0.5:
        new_animation = animation.replace(
            landing_lights_anim_hide,
            f"{landing_lights_anim_hide}\n{leading_whitespaces}{extra_anim_hide}",
        )

        if original_landinglights_anim_show != []:
            new_animation = new_animation.replace(
                f"{original_landinglights_anim_show[0]}\n", ""
            )

        return new_animation

    return animation

# TODO: Get rid of that bool here! Refactor this part and also in lights_updater main file.
# First get list of animations and than process them.
# def get_list_of_animations(object_content: str) -> list[str]:


def special_lights_treatment(object_content: str, convert_to_flashing_beacons: bool, aircraft_icao_type: str) -> str:
    """
    Treat some special light effects.

    1. Add missing taxilights on some airplanes.
       The original dataref for the taxilights is set to landing_lites_on instead of taxi_lites_on.

    2. Landing lights on front gear were visible even if that gear is retracted.
       ANIM_hide animation is added to the front gear landing lights.

    3. Based on switch -f / --flashing_beacons change beacons to be flashing

    Args:
        object_content (str): Original aricraft object content.

    Returns:
        object_content (str): Fixed aircraft object content.
    """
    animations: list[str] = re.findall(
        "(?s)(?=ANIM_begin)(.+?ANIM_end)", object_content
    )

    for animation in animations:
        # if is_front_gear_fix_done(animation):
        #     log.debug("Front gear lights already fixed.")
        #     continue
        # extra_anim_hide: str = (
        #     "ANIM_hide -1.000000 0.500000 libxplanemp/controls/gear_ratio"
        # )
        # if "airplane_taxi_pm" in animation:
        #     new_animation = fix_taxilights(animation)
        #     object_content = object_content.replace(animation, new_animation)
        # if "landing_lites" in animation:
        #     new_animation: str = fix_frontgear_landinglights(
        #         animation)
        #     if new_animation == animation:
        #         continue
        #     object_content = object_content.replace(animation, new_animation)
        if "airplane_beacon" in animation and convert_to_flashing_beacons is True:
            new_animation = convert_beacons_to_flashing_beacons(
                animation, aircraft_icao_type)
            object_content = object_content.replace(animation, new_animation)
            continue
    # Additional fixes for taxilights after the animations have been processed
    # object_content = correct_wrong_landing_lights_in_taxi_lights_animation(
    #     object_content)
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


def reduce_spill_intensity(line: str, reduce_light_type: str) -> str:
    """Reduces the groundspill intensity of a light

    Args:
        line (str): A string with light specific parameters
        strength (float): A factor to reduce the intensity by.

    Returns:
        str: A line with reduced intensity
    """
    reduce_factors = {
        "airplane_landing": 0.75,
        "airplane_taxi": 0.75,
        "airplane_nav": 0.40,
        "airplane_beacon": 0.35,
        "airplane_strobe": 0.50
    }

    split_line = line.split()
    intensity = int(split_line[9].replace("cd", ""))

    reduced_intensity = int(
        intensity * (reduce_factors[reduce_light_type]))
    split_line[9] = f"{str(reduced_intensity)}cd"
    line_to_return = " ".join(split_line)

    return line_to_return
