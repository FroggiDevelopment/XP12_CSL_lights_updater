from .common_lights_converter import convert_airplane_lights


def convert_airplane_nav_lights(animation: str, light_params_dict: dict[str, str]) -> str:
    """ Converts airplane nav lights

    Args:
        animation (str): The animations sequence with the nav lights
        nav_light_params_dict (dict[str, str]): The params for the nav lights

    Returns:
            str: The updated animations sequence with nav lights
    """
    light_type: str = "airplane_nav"

    new_animation = convert_airplane_lights(
        animation, light_params_dict, light_type)

    return new_animation
