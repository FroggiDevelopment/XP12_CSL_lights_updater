import pytest
from helpers.light_manipulators import convert_airplane_landing_lights

landing_light_param_dict = {
    'airplane_landing': ' 0.76052475 0.65837479 0.57758057 3 600000cd 0.034766696 0.052357007 -0.99802303 0.97629601'}


def test_renamed_to_light_param():
    animation = """
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
"""
    new_animation: str = animation.replace(
        'LIGHT_NAMED', 'LIGHT_PARAM')
    assert "LIGHT_NAMED" not in new_animation


def test_convert_airplane_landing_lights():
    start_animation = """
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
                """
    start_animation = start_animation.replace(
        'LIGHT_NAMED', 'LIGHT_PARAM')

    line_of_light = "LIGHT_PARAM airplane_landing_pm -2.1430 2.3514 0.0077  0.76052475 0.65837479 0.57758057 3 600000cd 0.034766696 0.052357007 -0.99802303 0.97629601"

    result = convert_airplane_landing_lights(
        start_animation, landing_light_param_dict)
    print(f"The result is:\n{result}")
    print(line_of_light in result)
    assert line_of_light in result
