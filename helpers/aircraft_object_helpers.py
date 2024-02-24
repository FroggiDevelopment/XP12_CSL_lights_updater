LIGHT_JETS = (
    "B733",
    "B734",
    "B737",
    "B738",
    "B739",
    "A318",
    "A319",
    "A320",
    "A321",
    "B462",
    "B463",
    "CRJ2",
    "CRJ7",
    "CRJ9",
    "CRJX",
    "E135",
    "E35L",
    "E145",
    "E170",
    "E175",
    "E190",
    "E195",
    "F100",
    "F28",
    "F70",
    "J328",
    "MD83",
    "MD90",
    "A320w",
    "A321w",
)
HEAVY_JETS = (
    "B717",
    "B744",
    "B74F",
    "B752",
    "B753",
    "B763",
    "B772",
    "B773",
    "B77L",
    "B77F",
    "B77W",
    "B788",
    "A306",
    "A310",
    "A332",
    "A333",
    "A337",
    "A342",
    "A343",
    "A345",
    "A346",
    "A359",
    "A388",
    "DC10",
    "MD11",
)
PROPS = ("DH8D", "AT42", "AT72", "D328", "F50", "JS41", "L410", "SB20", "SF34")


light_params = {
    "heavy": {
        "airplane_landing": "0.76052475 0.65837479 0.57758057 3 765000cd 0.034766696 -0.052357007 -0.99802303 0.97992471\n",
        "airplane_taxi": "0.76052475 0.65837479 0.57758057 3 400000cd 0.034766696 -0.052357007 -0.99802303 0.97992471\n",
        "airplane_nav_left": "0.94730663 0.82278603 0.7230553 0 500cd -0.077866882 -0.018656421 -0.99678928 0.34202015\n",
        "airplane_nav_right": "0.94730663 0.82278603 0.7230553 0 500cd -0.077866882 -0.018656421 -0.99678928 0.34202015\n",
        "airplane_nav_tail": "0.94730663 0.82278603 0.7230553 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015\n",
        "airplane_strobe": "3.7129087 -0.07354179 -1.1133618 1 1 1 0 75000cd 0.66745675 0.06932088 0.74141496 0.4617486\n",
        "airplane_beacon": "1 0 0 0 1000cd 0 0 0 1\n",
    },
    "light": {
        "airplane_landing": " 0.76052475 0.65837479 0.57758057 3 200000cd 0.034766696 -0.052357007 -0.99802303 0.97992471\n",
        "airplane_taxi": "0.76052475 0.65837479 0.57758057 3 100000cd 0.034766696 -0.052357007 -0.99802303 0.97992471\n",
        "airplane_nav_left": "0.94730663 0.82278603 0.7230553 0 500cd -0.077866882 -0.018656421 -0.99678928 0.34202015\n",
        "airplane_nav_right": "0.94730663 0.82278603 0.7230553 0 500cd -0.077866882 -0.018656421 -0.99678928 0.34202015\n",
        "airplane_nav_tail": "0.94730663 0.82278603 0.7230553 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015\n",
        "airplane_strobe": "3.7129087 -0.07354179 -1.1133618 1 1 1 0 75000cd 0.66745675 0.06932088 0.74141496 0.4617486\n",
        "airplane_beacon": "1 0 0 0 1000cd 0 0 0 1\n",
    },
    "props": {
        "airplane_landing": " 0.76052475 0.65837479 0.57758057 3 150000cd 0.034766696 -0.052357007 -0.99802303 0.97992471\n",
        "airplane_taxi": "0.76052475 0.65837479 0.57758057 3 80000cd 0.034766696 -0.052357007 -0.99802303 0.97992471\n",
        "airplane_nav_left": "0.94730663 0.82278603 0.7230553 0 500cd -0.077866882 -0.018656421 -0.99678928 0.34202015\n",
        "airplane_nav_right": "0.94730663 0.82278603 0.7230553 0 500cd -0.077866882 -0.018656421 -0.99678928 0.34202015\n",
        "airplane_nav_tail": "0.94730663 0.82278603 0.7230553 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015\n",
        "airplane_strobe": "3.7129087 -0.07354179 -1.1133618 1 1 1 0 75000cd 0.66745675 0.06932088 0.74141496 0.4617486\n",
        "airplane_beacon": "1 0 0 0 1000cd 0 0 0 1\n",
    },
}


def determine_light_params(aircraft_type: str, light_type: str = "default") -> str:
    """Determines the paramaters for the given aircraft type

    Args:
        aircraft_type (str): Aircraft type e.g. B733 for Boeing 737-300

    Returns:
        str: A string with the corresponding light parameters for the given aircraft type
    """

    light_specific_params = ""
    if light_type == "default":
        return ""
    if aircraft_type in HEAVY_JETS:
        light_specific_params = light_params["heavy"]
    if aircraft_type in LIGHT_JETS:
        light_specific_params = light_params["light"]
    if aircraft_type in PROPS:
        light_specific_params = light_params["props"]

    return light_specific_params
