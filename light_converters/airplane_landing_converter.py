from .base_converter import convert_airplane_lights


def convert_airplane_landing_lights(animation: str, light_params_dict: dict[str, str]) -> str:
    """ Converts airplane lights

    Args:
        animation (str): The animations sequence with the XP11 lights
        light_params_dict (dict[str, str]): The params for the XP12 lights

    Returns:
            str: The updated animations sequence with XP12 lights
    """
    light_type = "airplane_landing"
    new_animation = convert_airplane_lights(
        animation, light_params_dict, light_type)
    return new_animation
