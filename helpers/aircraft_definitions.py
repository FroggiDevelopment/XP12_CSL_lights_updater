def set_aircraft_data():
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
    GA = (
        "BE20",
        "C150",
        "C172",
        "C182",
        "C421",
    )
    PRIVATE_JETS = (
        "LJ45",
        "H25B",
    )
    HELI = (
        "B06",
        "EC35",
        "S76",
    )
    MIL_FIGHTER = (
        "F16C",
        "F16D",
        "F18C",
        "F18D",
        "HAWK",
        "M339",
        "MG29",
        "SU27",
        "TOR",
        "EUFI",
    )
    MIL_HEAVY_JETS = (
        "C17",
        "C5M",
        "E3D",
    )
    MIL_HEAVY_PROPS = (
        "C130",
        "C30J",
        "A400",
    )
    MIL_LIGHT_PROPS = (
        "G115",
        "CL41",
        "TUCA",
        "PC9",
    )

    light_params = {
        "heavy": {
            "airplane_landing": "0.76052475 0.65837479 0.57758057 3 800000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
            "airplane_taxi": "0.76052475 0.65837479 0.57758057 3 400000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
            "airplane_nav_left": "0.89626974 0.099898659 0 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
            "airplane_nav_right": "0.020288363 0.73791075 0.36130685 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
            "airplane_nav_tail": "0.94730663 0.82278603 0.7230553 0 3000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
            "airplane_strobe": "3.7129087 -0.07354179 -1.1133618 1 1 1 0 75000cd 0.66745675 0.06932088 0.74141496 0.4617486",
            "airplane_beacon": "1 0 0 0 1000cd 0 0 0 1",
        },
        "light": {
            "airplane_landing": " 0.76052475 0.65837479 0.57758057 3 700000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
            "airplane_taxi": "0.76052475 0.65837479 0.57758057 3 300000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
            "airplane_nav_left": "0.89626974 0.099898659 0 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
            "airplane_nav_right": "0.020288363 0.73791075 0.36130685 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
            "airplane_nav_tail": "0.94730663 0.82278603 0.7230553 0 3000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
            "airplane_strobe": "3.7129087 -0.07354179 -1.1133618 1 1 1 0 75000cd 0.66745675 0.06932088 0.74141496 0.4617486",
            "airplane_beacon": "1 0 0 0 1000cd 0 0 0 1",
        },
        "private_jets": {
            "airplane_landing": " 0.76052475 0.65837479 0.57758057 3 500000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
            "airplane_taxi": "0.76052475 0.65837479 0.57758057 3 100000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
            "airplane_nav_left": "0.89626974 0.099898659 0 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
            "airplane_nav_right": "0.020288363 0.73791075 0.36130685 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
            "airplane_nav_tail": "0.94730663 0.82278603 0.7230553 0 3000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
            "airplane_strobe": "3.7129087 -0.07354179 -1.1133618 1 1 1 0 75000cd 0.66745675 0.06932088 0.74141496 0.4617486",
            "airplane_beacon": "1 0 0 0 1000cd 0 0 0 1",
        },
        "props": {
            "airplane_landing": " 0.76052475 0.65837479 0.57758057 3 500000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
            "airplane_taxi": "0.76052475 0.65837479 0.57758057 3 50000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
            "airplane_nav_left": "0.89626974 0.099898659 0 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
            "airplane_nav_right": "0.020288363 0.73791075 0.36130685 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
            "airplane_nav_tail": "0.94730663 0.82278603 0.7230553 0 3000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
            "airplane_strobe": "3.7129087 -0.07354179 -1.1133618 1 1 1 0 75000cd 0.66745675 0.06932088 0.74141496 0.4617486",
            "airplane_beacon": "1 0 0 0 1000cd 0 0 0 1",
        },
        "general_aviation": {
            "airplane_landing": " 0.76052475 0.65837479 0.57758057 3 300000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
            "airplane_taxi": "0.76052475 0.65837479 0.57758057 3 50000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
            "airplane_nav_left": "0.89626974 0.099898659 0 0 700cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
            "airplane_nav_right": "0.020288363 0.73791075 0.36130685 0 7000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
            "airplane_nav_tail": "0.94730663 0.82278603 0.7230553 0 1500cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
            "airplane_strobe": "3.7129087 -0.07354179 -1.1133618 1 1 1 0 5000cd 0.66745675 0.06932088 0.74141496 0.4617486",
            "airplane_beacon": "1 0 0 0 1000cd 0 0 0 1",
        },
        "heli": {
            "airplane_landing": " 0.76052475 0.65837479 0.57758057 3 200000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
            "airplane_taxi": "0.76052475 0.65837479 0.57758057 3 50000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
            "airplane_nav_left": "0.89626974 0.099898659 0 0 700cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
            "airplane_nav_right": "0.020288363 0.73791075 0.36130685 0 7000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
            "airplane_nav_tail": "0.94730663 0.82278603 0.7230553 0 1500cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
            "airplane_strobe": "3.7129087 -0.07354179 -1.1133618 1 1 1 0 5000cd 0.66745675 0.06932088 0.74141496 0.4617486",
            "airplane_beacon": "1 0 0 0 1000cd 0 0 0 1",
        },
    }
    return (
        light_params,
        LIGHT_JETS,
        HEAVY_JETS,
        PRIVATE_JETS,
        GA,
        PROPS,
        MIL_FIGHTER,
        MIL_HEAVY_JETS,
        MIL_HEAVY_PROPS,
        MIL_LIGHT_PROPS,
        HELI,
    )


def determine_light_params(aircraft_type: str, light_type: str = "") -> str:
    """Determines the paramaters for the given aircraft type

    Args:
        aircraft_type (str): Aircraft type e.g. B733 for Boeing 737-300

    Returns:
        str: A string with the corresponding light parameters for the given aircraft type
    """
    (
        light_params,
        LIGHT_JETS,
        HEAVY_JETS,
        PRIVATE_JETS,
        GA,
        PROPS,
        MIL_FIGHTER,
        MIL_HEAVY_JETS,
        MIL_HEAVY_PROPS,
        MIL_LIGHT_PROPS,
        HELI,
    ) = set_aircraft_data()
    light_specific_params = ""

    if light_type == "":
        raise ValueError("The light type is missing!")
    if aircraft_type == "":
        raise ValueError("The aircraft type is missing!")
    if aircraft_type in HEAVY_JETS:
        light_specific_params = light_params["heavy"]
    if aircraft_type in LIGHT_JETS:
        light_specific_params = light_params["light"]
    if aircraft_type in PRIVATE_JETS:
        light_specific_params = light_params["private_jets"]
    if aircraft_type in PROPS:
        light_specific_params = light_params["props"]
    if aircraft_type in GA:
        light_specific_params = light_params["general_aviation"]
    if aircraft_type in HELI:
        light_specific_params = light_params["heli"]
    if aircraft_type in MIL_HEAVY_JETS:
        light_specific_params = light_params["heavy"]
    if aircraft_type in MIL_FIGHTER:
        light_specific_params = light_params["light"]
    if aircraft_type in MIL_HEAVY_PROPS:
        light_specific_params = light_params["props"]
    if aircraft_type in MIL_LIGHT_PROPS:
        light_specific_params = light_params["general_aviation"]
    if light_specific_params == "":
        light_specific_params = light_params[
            "light"
        ]  # If all fails, give the aircraft some light.
    return light_specific_params
