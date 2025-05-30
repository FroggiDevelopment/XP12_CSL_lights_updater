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
from helpers.custom_exceptions import WrongLightInAnimationError

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

STANDARD_AIRPLANE_LIGHTS = [
    "airplane_landing",
    "airplane_taxi",
    "airplane_nav",
    "airplane_beacon",
    "airplane_flashing",
    "airplane_strobe",
]

# Setup logging
init_logging()
log = logging.getLogger(__name__)

# aircraft_categories = get_aircraft_categories()


def is_wrong_light_in_animation(animation: str, good_light: str) -> bool:
    """ Check if the animation contains a light that should not be in it
        Creates a list of bad lights based on STANDARD_AIRPLANE_LIGHTS
        and good_light

    Args:
        animation (str): The animation to check
        good_light (str): The light that should be in it

    Returns:
        bool: True if the animation contains a light that should not be in it
    """
    _bad_lights = [
        bad_light for bad_light in STANDARD_AIRPLANE_LIGHTS if bad_light not in good_light]
    if any(_bad_lights in animation for _bad_lights in _bad_lights):
        return True
    return False


def uncomment_light_line(line: str) -> str:
    """Uncomments the light param line

    Args:
        line (str): line with light params

    Returns:
        str: uncommented line with light params
    """
    if "#LIGHT_" in line:
        return line.replace("#", "")
    return line


def get_light_coordinates(line: str) -> str:
    """ Get the coordinates of the light source

    Args:
        line (str): line with light params

    Returns:
        str: coordinates of the lightsource
    """
    return f"{':'.join(line.split()[2:5])}"


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


def convert_airplane_landing_lights(animation: str, landing_light_params_dict: dict[str, str]) -> str:
    """ Converts airplane landing lights

    Args:
        animation (str): The animations sequence with the landing lights
        landing_light_params_dict (dict[str, str]): The params for the landing lights

    Returns:
            str: The updated animations sequence with landing lights
    """

    _OLD_LANDING_LIGHTS = [
        "airplane_landing_core ",
        "airplane_landing_glow ",
        "airplane_landing_flare ",
        "airplane_landing_sp",
        "airplane_landing0 ",
        "airplane_landing1 ",
        "airplane_landing2 ",
        "airplane_landing3 ",
        "airplane_landing_size ",
        "airplane_landing_flash ",
        "PLN_airplane_landing "
    ]

    _GOOD_LANDING_LIGHTS = [
        "airplane_landing_bb ",
        "airplane_landing_pm ",
        "airplane_landing "
    ]

    animation = animation.replace("\t", "    ")
    if re.findall(r"LIGHT_PARAM.+airplane_landing", animation) == []:
        return animation
    # TODO: Can be refactored to be one function on its own????? Will it work for all lights? I think so!!
    if any(good_landing in animation for good_landing in _GOOD_LANDING_LIGHTS):
        pass
    else:
        if any((gotcha := old_landing) in animation for old_landing in _OLD_LANDING_LIGHTS):
            searchstring = fr"^\s*LIGHT_PARAM\s+{gotcha}.*$"
            matching_light_line = re.search(searchstring,
                                            animation, re.MULTILINE)
            if matching_light_line:
                line_to_replace = matching_light_line.group()

                replaced_line = line_to_replace.replace(
                    gotcha, 'airplane_landing ')
                animation = animation.replace(
                    line_to_replace, replaced_line, 1)
    for line in animation.splitlines():
        leading_whitespaces = get_leading_whitespaces(line)

        if "airplane_landing_" in line:
            animation = animation.replace(line, "")
            continue

        if "airplane_landing" in line:
            # Remove possible comment sign
            new_line = uncomment_light_line(line)
            new_line = new_line.replace(
                "airplane_landing", "airplane_landing_bb")
            just_light = get_basic_light_params(new_line)

            new_light_line = f"{leading_whitespaces}{just_light} {landing_light_params_dict['airplane_landing']}"

            spill_line = create_spill_lines(new_light_line, "airplane_landing")

            animation = animation.replace(
                line, new_light_line + "\n" + leading_whitespaces + spill_line)

    new_animation = os.linesep.join(
        [line for line in animation.splitlines() if line])

    # Fix landing lights on frontgear
    if is_front_gear_fix_done is False:
        new_animation = fix_frontgear_landinglights(new_animation)

    return new_animation


def convert_airplane_taxi_lights(animation: str, taxi_light_params_dict: dict[str, str]) -> str:
    """ Converts airplane taxi lights to XP12 standard

    Args:
        animation (str): The animations sequence with the taxi lights
        taxi_light_params_dict (dict[str, str]): The params for the taxi lights

    Returns:
            str: The updated animations sequence with taxi lights
    """

    _GOOD_TAXI_LIGHTS = [
        "airplane_taxi ",
        "airplane_taxi_bb ",
        "airplane_taxi_pm "
    ]

    _OLD_TAXI_LIGHTS = [
        "airplane_taxi_bb",
        "airplane_taxi_core",
        "airplane_taxi_glow",
        "airplane_taxi_flare",
        "airplane_taxi_sp",
        "airplane_taxi_size",
        "airplane_taxi_flash",
        "PLN_airplane_taxi",
    ]

    animation = animation.replace("\t", "    ")

    if any(good_taxi in animation for good_taxi in _GOOD_TAXI_LIGHTS):
        pass
    else:
        if any((gotcha := old_taxi) in animation for old_taxi in _OLD_TAXI_LIGHTS):
            searchstring = fr"^\s*LIGHT_PARAM\s+{gotcha}.*$"
            matching_light_line = re.search(searchstring,
                                            animation, re.MULTILINE)
            if matching_light_line:
                line_to_replace = matching_light_line.group()

                replaced_line = line_to_replace.replace(
                    gotcha, 'airplane_taxi ')
                animation = animation.replace(
                    line_to_replace, replaced_line, 1)

    for line in animation.splitlines():
        leading_whitespaces = get_leading_whitespaces(line)
        # TODO: Maybe creating airplane taxi lights from none standard here is also necessary? To be checked....
        if "airplane_taxi_" in line:
            animation = animation.replace(line, "")
            continue

        # As there are rare cases of landing lights in these animations... fix it!
        if "airplane_landing" in line:
            line = line.replace("airplane_landing", "airplane_taxi")

        if "airplane_taxi" in line:
            # Remove possible comment sign
            new_line = uncomment_light_line(line)
            new_line = new_line.replace("airplane_taxi", "airplane_taxi_bb")
            just_light = get_basic_light_params(new_line)
            new_light_line = f"{leading_whitespaces}{just_light} {taxi_light_params_dict['airplane_taxi']}"
            spill_line = create_spill_lines(new_light_line, "airplane_taxi")
            animation = animation.replace(
                line, new_light_line + "\n" + leading_whitespaces + spill_line)

    new_animation = os.linesep.join(
        [line for line in animation.splitlines() if line])

    # Add ANIM_hide animation to hide when rectracted
    if is_front_gear_fix_done(new_animation) is False:
        new_animation = fix_taxilights(new_animation)
    return new_animation


def convert_airplane_nav_lights(animation: str, nav_light_params_dict: dict[str, str]) -> str:
    """ Converts airplane nav lights

    Args:
        animation (str): The animations sequence with the nav lights
        nav_light_params_dict (dict[str, str]): The params for the nav lights

    Returns:
            str: The updated animations sequence with nav lights
    """
    # Sometimes the lights are wrong in this animation. It's a shame!
    if is_wrong_light_in_animation(animation, good_light="airplane_nav"):
        raise WrongLightInAnimationError(
            f"This animation contains the wrong light type for airplane_nav!\n{animation}")

    _GOOD_NAVS = [
        "airplane_nav ",
        "airplane_nav_bb",
        "airplane_nav_pm",
        "airplane_nav_right ",
        "airplane_nav_left ",
        "airplane_nav_tail "
    ]

    _OLD_NAVS = [
        "airplane_nav_tail_size",
        "airplane_nav_left_size",
        "airplane_nav_right_size",
        "airplane_nav_sp",
        "airplane_nav_tail_static_h",
        "airplane_nav_left_static_h",
        "airplane_nav_right_static_h",
        "airplane_nav_tail_static",
        "airplane_nav_left_static",
        "airplane_nav_right_static",
        "PLN_airplane_nav_tail",
        "PLN_airplane_nav_left",
        "PLN_airplane_nav_right",
    ]

    # Get rid of tabs...
    animation = animation.replace("\t", "    ")

    # Check if normal airplane_navs are available in animation, else take first other nav light line to create it!!
    if any(good_nav in animation for good_nav in _GOOD_NAVS):
        pass
    else:
        if any(old_nav in animation for old_nav in _OLD_NAVS):
            matching_light_lines: list[str] = re.findall(r'^\s*LIGHT_PARAM\s+airplane_nav_.*$',
                                                         animation, re.MULTILINE)
            for match in matching_light_lines:
                if "airplane_nav_sp" in match:
                    animation = animation.replace(
                        match,
                        match.replace("airplane_nav_sp", "airplane_nav "),
                    )
        # TODO: Errorhandling if no nav light is found??
    for line in animation.splitlines():

        leading_whitespaces = get_leading_whitespaces(line)

        if any(old_navs in line for old_navs in _OLD_NAVS):
            animation = animation.replace(line, "")
            continue

        if "airplane_nav" in line:
            # Remove possible comment sign
            new_line = uncomment_light_line(line)

            # Add positional arguments to the line if it is missing
            if not any(positional_argument in line for positional_argument in POSITION_IDENTIFIERS):
                new_line = add_lateral_position_to_lights(line)

            nav_light_with_position = new_line.split()[1]
            nav_light_params = nav_light_params_dict[nav_light_with_position]

            just_light = get_basic_light_params(new_line)
            new_line = f"{just_light} {nav_light_params}"

            # Remove positional arguments from the line
            if any((position := positional_argument) in new_line for positional_argument in POSITION_IDENTIFIERS):
                new_line = new_line.replace(position, "")

            new_line = new_line.replace("airplane_nav", "airplane_nav_bb")

            spill_line = create_spill_lines(new_line, "airplane_nav")
            new_line = f"{leading_whitespaces}{new_line}\n{leading_whitespaces}{spill_line}"

            animation = animation.replace(line, new_line)

    new_animation = os.linesep.join(
        [line for line in animation.splitlines() if line])

    return new_animation


def convert_airplane_beacon_lights(animation: str, beacon_light_params_dict: dict[str, str]) -> str:
    """ Converts airplane beacon lights

     Args:
         animation (str): The animations sequence with the beacon lights
         beacon_light_params_dict (dict[str, str]): The params for the beacon lights

     Returns:
             str: The updated animations sequence with beacon lights
     """

    _OLD_BEACONS = [
        "airplane_beacon_rotate",
        "airplane_beacon_rotate_sp",
        "airplane_beacon_strobe",
        "airplane_beacon_strobe_sp",
        "airplane_beacon_sp",
        "airplane_beacon_size",
    ]

    # _GOOD_BEACONS = [
    #     "airplane_beacon",
    #     "airplane_beacon_bb",
    #     "airplane_beacon_pm"
    # ]

    known_light_coordinates: list[str] = []

    for line in animation.splitlines():
        if "airplane_beacon" in line:
            leading_whitespaces = get_leading_whitespaces(line)
            # Remove comment sign
            new_line = uncomment_light_line(line)
            light_source_coordinates = get_light_coordinates(new_line)

            if light_source_coordinates in known_light_coordinates:
                log.debug(
                    f"Navigation light at {light_source_coordinates} already converted!")
                new_line = ""
            else:
                known_light_coordinates.append(light_source_coordinates)

                # For the time beeing only "normal" beacon lights are supported
                if any((change_beacon := old_beacon) in line for old_beacon in _OLD_BEACONS):
                    new_line = line.replace(change_beacon, "airplane_beacon")

                new_line = new_line.replace(
                    "airplane_beacon", "airplane_beacon_bb")

                just_light = get_basic_light_params(new_line)

                new_light_line = f"{just_light} {beacon_light_params_dict['airplane_beacon']}"

                spill_line = create_spill_lines(
                    new_light_line, "airplane_beacon")

                new_line = f"{leading_whitespaces}{new_light_line}\n{leading_whitespaces}{spill_line}"

            animation = animation.replace(line, new_line)

    new_animation = os.linesep.join(
        [line for line in animation.splitlines() if line])

    return new_animation


def convert_airplane_flashing_beacon_lights(animation: str, beacon_light_params_dict: dict[str, str]) -> str:
    """ Converts airplane beacon lights to flashing beacons

     Args:
         animation (str): The animations sequence with the beacon lights
         beacon_light_params_dict (dict[str, str]): The beacon light parameters

     Returns:
             str: The updated animations sequence with flashing beacon lights
     """
    new_animation = convert_airplane_beacon_lights(
        animation, beacon_light_params_dict)

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

    original_beacon_anim_hide = re.findall(
        "ANIM_hide.+libxplanemp/controls/beacon_lites_on", new_animation)

    if original_beacon_anim_hide != []:
        new_animation = new_animation.replace(
            original_beacon_anim_hide[0], new_anim_hide)

    new_animation = new_animation.replace(
        "airplane_beacon", "airplane_generic")

    new_animation = increase_flashing_beacon_light_intensity(new_animation)

    return new_animation


def convert_airplane_strobe_lights(animation: str, strobe_light_params_dict: dict[str, str]) -> str:
    """Converts airplane strobe lights

    Args:
        animation (str): The animations sequence with the strobe lights
        strobe_light_params_dict (dict[str, str]): The params for the strobe lights

    Returns:
        str: The updated animations sequence with strobe lights
    """
    _GOOD_STROBES = [
        "airplane_strobe ",
        "airplane_strobe_bb ",
        "airplane_strobe_pm "
    ]

    _OLD_STROBES = [
        "airplane_strobe_omni",
        "airplane_strobe_dir",
        "airplane_strobe_sp",
        "airplane_strobe_size",
        "PLN_airplane_strobe",
    ]
    animation = animation.replace("\t", "    ")
    # Check if normal airplane strobes are available in animation or take first other strobe light line to create it!
    if any(good_strobe in animation for good_strobe in _GOOD_STROBES):
        pass
    else:
        if any(old_strobe in animation for old_strobe in _OLD_STROBES):
            matching_light_lines: list[str] = re.findall(r'^\s*LIGHT_PARAM\s+airplane_strobe_.*$',
                                                         animation, re.MULTILINE)
            for match in matching_light_lines:
                if "airplane_strobe_sp" in match:
                    animation = animation.replace(
                        match,
                        match.replace("airplane_strobe_sp",
                                      "airplane_strobe "),
                    )

    for line in animation.splitlines():

        leading_whitespaces = get_leading_whitespaces(line)

        if any(old_strobes in line for old_strobes in _OLD_STROBES):
            animation = animation.replace(line, "")
            continue

        if "airplane_strobe" in line:
            # Remove possible comment sign
            new_line = uncomment_light_line(line)

            # Add positional arguments to the line if it is missing
            if not any(positional_argument in new_line for positional_argument in POSITION_IDENTIFIERS):
                new_line = add_lateral_position_to_lights(new_line)

            strobe_light_with_position = new_line.split()[1]
            strobe_light_params = strobe_light_params_dict[strobe_light_with_position]

            just_light = get_basic_light_params(new_line)
            new_line = f"{just_light} {strobe_light_params}"

            # Remove positional arguments from the line
            if any((position := positional_argument) in new_line for positional_argument in POSITION_IDENTIFIERS):
                new_line = new_line.replace(position, "")

            new_line = new_line.replace(
                "airplane_strobe", "airplane_strobe_bb")

            spill_line = create_spill_lines(new_line, "airplane_strobe")
            new_line = f"{leading_whitespaces}{new_line}\n{leading_whitespaces}{spill_line}"

            animation = animation.replace(line, new_line)

    new_animation = os.linesep.join(
        [line for line in animation.splitlines() if line])

    return new_animation


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

    for light_intensity in unique_light_intensity_list:
        original_candelar = float(light_intensity.replace("cd", ""))
        increased_candelar = original_candelar * increase_beacon_intensity_factor
        new_light_intensity = f"{increased_candelar}cd"
        animation = animation.replace(
            light_intensity, new_light_intensity)
    return animation


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

    if original_taxi_anim_hide != []:
        leading_whitespaces = get_leading_whitespaces(
            original_taxi_anim_hide[0])
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
