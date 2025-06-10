import re
import os
from helpers import get_light_params_for_aircraft_type
from helpers.light_manipulators import reduce_spill_intensity


def airplane_landing_converter(animation: str, landing_light_params_dict: dict[str, str]) -> str:
    _known_coordinates: list[str] = []
    animation.replace("\t", "....")
    # animation = animation.replace("LIGHT_NAMED", "LIGHT_PARAM")

    for line in animation.splitlines():
        if "airplane_landing" in line:
            coordinates = f"{line.split()[2]}    {line.split()[3]}    {line.split()[4]}"
            if coordinates in _known_coordinates:
                animation = animation.replace(line, "")
                continue
            _known_coordinates.append(coordinates)
            line_start = "LIGHT_PARAM    airplane_landing_bb"
            line_end = f"{landing_light_params_dict['airplane_landing']}"

            new_line = f"{line_start}   {coordinates}   {line_end}"
            spill_line = new_line.replace("_bb", "_pm")
            spill_line = reduce_spill_intensity(
                spill_line, "airplane_landing")

            new_line = f"{new_line}\n{spill_line}"

            animation = animation.replace(line, new_line)

    # remove empty lines
    new_animation = os.linesep.join(
        [line for line in animation.splitlines() if line])

    return new_animation


object_content = """
ANIM_begin
    ANIM_hide	-1.0 0.0	libxplanemp/controls/landing_lites_on
    #LIGHT_NAMED	airplane_landing	 2.1435    2.3514    0.0077
    LIGHT_PARAM	airplane_landing_core	 2.1435    2.3514    0.0077	0 0 -1 1 0.4
    LIGHT_PARAM	airplane_landing_glow	 2.1435    2.3514    0.0077 0 0 -1 1 0.5
    LIGHT_PARAM	airplane_landing_flare	 2.1435    2.3514    0.0077	0 0 -1 1 1.0
    LIGHT_PARAM	airplane_landing_sp	 2.1435    2.3514    0.0077	2 2 2.5 1 300 0.7
    #LIGHT_NAMED	airplane_landing	-2.1430    2.3514    0.0077
    LIGHT_PARAM	airplane_landing_core	-2.1430    2.3514    0.0077	0 0 -1 1 0.4
    LIGHT_PARAM	airplane_landing_glow	-2.1430    2.3514    0.0077 0 0 -1 1 0.5
    LIGHT_PARAM	airplane_landing_flare	-2.1430    2.3514    0.0077	0 0 -1 1 1.0
    LIGHT_PARAM	airplane_landing_sp	-2.1430    2.3514    0.0077	2 2 2.5 1 300 0.7
ANIM_end
# airplane_landing
ANIM_begin
        ANIM_hide	-1.0 0.0	libxplanemp/controls/landing_lites_on
    ANIM_hide	-1.0 0.95	libxplanemp/controls/gear_ratio
        LIGHT_PARAM	airplane_landing_core	-0.2111    1.7590  -11.2932	0 0 -1 1 0.4
        LIGHT_PARAM	airplane_landing_glow	-0.2111    1.7590  -11.2932 0 0 -1 1 0.5
        LIGHT_PARAM	airplane_landing_flare	-0.2111    1.7590  -11.2932	0 0 -1 1 1.0
ANIM_end
"""

light_params_dict: dict[str, dict[str, str]] = get_light_params_for_aircraft_type(
    str("B733")
)

animations: list[str] = re.findall(
    r"(?s)(?=ANIM_begin)(.+?ANIM_end)", object_content)

for animation in animations:
    new_animation = airplane_landing_converter(
        animation, light_params_dict["airplane_landing"])
    print(new_animation)
