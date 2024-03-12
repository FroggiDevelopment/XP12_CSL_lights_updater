import logging

logger = logging.getLogger(__name__)

aircrafts: dict = {
    "airliners": {
        "B733",
        "B733fa",
        "B733ai",
        "B734",
        "B735",
        "B735fa",
        "B735wfa",
        "B737",
        "B738",
        "B738s",
        "B738WLai",
        "B738WLfa",
        "B738fa",
        "B738ai",
        "B739",
        "B739WLfa",
        "B739fa",
        "B739s",
        "A318",
        "A318fCFM",
        "A318dCFM",
        "A319",
        "A321fCFM",
        "A321fIAE",
        "A319fCFM",
        "A319dCFM",
        "A319dIAE",
        "A319fIAE",
        "A321wfCFM",
        "A321wfIAE",
        "A320fCFM",
        "A320CFM",
        "A320IAE",
        "A320fIAE",
        "A319fCFMw",
        "A319fIAEw",
        "A320wCFM",
        "A320wIAE",
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
        "E145p1",
        "E170",
        "E175",
        "E190",
        "E195",
        "F100",
        "F28",
        "F70",
        "J328",
        "MD81",
        "MD83",
        "MD90",
        "A319f",
        "A320w",
        "A321w",
        "AN72",
        "AN74",
        "IL62",
        "SU95",
        "TU134",
        "TU154",
        "TU204",
        "T154",
    },
    "heavy_airliners": {
        "B717",
        "B744",
        "B744Fge",
        "B744Fpw",
        "B744Frr",
        "B744rr",
        "B74F",
        "B744ge",
        "B744pw",
        "B748Ffa",
        "B752",
        "B752RR",
        "B752PWold",
        "B752RRold",
        "B752PW",
        "B753",
        "B753RRold",
        "B753PWold",
        "B752PWwold",
        "B752RRwold",
        "B753PWw",
        "B753RRw",
        "B752PWw",
        "B752RRw",
        "B763",
        "B763aiGEw",
        "B763aiPWw",
        "B763aiGE",
        "B763aiPW",
        "B763aiRR",
        "B772",
        "B773",
        "B77L",
        "B77F",
        "B77W",
        "B788",
        "B789",
        "A3ST",
        "A306",
        "A306PW",
        "A310",
        "A332",
        "A332RRold",
        "A332GEnew",
        "A332RRnew",
        "A332GEold",
        "A332PWnew",
        "A332PWold",
        "A333",
        "A333RR",
        "A333GE",
        "A333PW",
        "A337",
        "A342",
        "A343",
        "A345",
        "A346",
        "A359",
        "A388",
        "A388fuse",
        "DC10",
        "MD11",
        "AN225",
        "IL86",
        "IL96",
        "C17",
        "C5M",
        "C5",
        "E3D",
        "IL76",
        "DC10",
        "MD11",
        "CONC",
        "T144",
        "B748fa",
        "B772GE",
        "B764aiGE",
        "IL76a50",
    },
    "props": {
        "DH8D",
        "AT42",
        "AT72",
        "AT75",
        "D328",
        "E120",
        "F50",
        "JS41",
        "L410",
        "SB20",
        "SF34",
        "AN12",
        "AN22",
        "AN24",
        "AN26",
        "AN28",
        "AN30",
        "AN32",
        "AN8",
        "C130",
        "C130HL",
        "C130HT",
        "C130H",
        "C30J",
        "A400",
    },
    "general_aviation": {
        "BE20",
        "C150",
        "C172",
        "C182",
        "C421",
        "G115",
        "CL41",
        "TUCA",
        "PC9",
        "SR22",
        "BE58",
        "C208",
        "C208cp",
        "PC12",
        "SF50",
    },
    "private_jets": {
        "LJ45",
        "H25B",
        "C750",
        "F900",
        "F900W",
    },
    "heli": {
        "B06",
        "EC35",
        "EC75",
        "S76",
        "Mi26",
        "AS350",
    },
    "fighter_jets": {
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
        "F35",
        "F22",
    },
}


light_params = {
    "heavy_airliners": {
        "airplane_landing": "0.76052475 0.65837479 0.57758057 3 800000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
        "airplane_taxi": "0.76052475 0.65837479 0.57758057 3 400000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
        "airplane_nav": "0.89626974 0.099898659 0 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_nav_left": "0.89626974 0.099898659 0 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_nav_right": "0.020288363 0.73791075 0.36130685 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_nav_tail": "0.94730663 0.82278603 0.7230553 0 3000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_strobe": "3.7129087 -0.07354179 -1.1133618 1 1 1 0 75000cd 0.66745675 0.06932088 0.74141496 0.4617486",
        "airplane_beacon": "1 0 0 0 5000cd 0 0 0 1",
    },
    "airliners": {
        "airplane_landing": " 0.76052475 0.65837479 0.57758057 3 800000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
        "airplane_taxi": "0.76052475 0.65837479 0.57758057 3 300000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
        "airplane_nav": "0.89626974 0.099898659 0 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_nav_left": "0.89626974 0.099898659 0 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_nav_right": "0.020288363 0.73791075 0.36130685 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_nav_tail": "0.94730663 0.82278603 0.7230553 0 3000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_strobe": "3.7129087 -0.07354179 -1.1133618 1 1 1 0 75000cd 0.66745675 0.06932088 0.74141496 0.4617486",
        "airplane_beacon": "1 0 0 0 5000cd 0 0 0 1",
    },
    "private_jets": {
        "airplane_landing": " 0.76052475 0.65837479 0.57758057 3 600000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
        "airplane_taxi": "0.76052475 0.65837479 0.57758057 3 100000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
        "airplane_nav": "0.89626974 0.099898659 0 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_nav_left": "0.89626974 0.099898659 0 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_nav_right": "0.020288363 0.73791075 0.36130685 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_nav_tail": "0.94730663 0.82278603 0.7230553 0 3000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_strobe": "3.7129087 -0.07354179 -1.1133618 1 1 1 0 75000cd 0.66745675 0.06932088 0.74141496 0.4617486",
        "airplane_beacon": "1 0 0 0 5000cd 0 0 0 1",
    },
    "fighter_jets": {
        "airplane_landing": " 0.76052475 0.65837479 0.57758057 3 500000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
        "airplane_taxi": "0.76052475 0.65837479 0.57758057 3 100000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
        "airplane_nav": "0.89626974 0.099898659 0 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_nav_left": "0.89626974 0.099898659 0 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_nav_right": "0.020288363 0.73791075 0.36130685 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_nav_tail": "0.94730663 0.82278603 0.7230553 0 3000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_strobe": "3.7129087 -0.07354179 -1.1133618 1 1 1 0 75000cd 0.66745675 0.06932088 0.74141496 0.4617486",
        "airplane_beacon": "1 0 0 0 5000cd 0 0 0 1",
    },
    "props": {
        "airplane_landing": " 0.76052475 0.65837479 0.57758057 3 600000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
        "airplane_taxi": "0.76052475 0.65837479 0.57758057 3 50000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
        "airplane_nav": "0.89626974 0.099898659 0 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_nav_left": "0.89626974 0.099898659 0 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_nav_right": "0.020288363 0.73791075 0.36130685 0 1000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_nav_tail": "0.94730663 0.82278603 0.7230553 0 3000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_strobe": "3.7129087 -0.07354179 -1.1133618 1 1 1 0 75000cd 0.66745675 0.06932088 0.74141496 0.4617486",
        "airplane_beacon": "1 0 0 0 5000cd 0 0 0 1",
    },
    "general_aviation": {
        "airplane_landing": " 0.76052475 0.65837479 0.57758057 3 400000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
        "airplane_taxi": "0.76052475 0.65837479 0.57758057 3 50000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
        "airplane_nav": "0.89626974 0.099898659 0 0 700cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_nav_left": "0.89626974 0.099898659 0 0 700cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_nav_right": "0.020288363 0.73791075 0.36130685 0 7000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_nav_tail": "0.94730663 0.82278603 0.7230553 0 1500cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_strobe": "3.7129087 -0.07354179 -1.1133618 1 1 1 0 5000cd 0.66745675 0.06932088 0.74141496 0.4617486",
        "airplane_beacon": "1 0 0 0 5000cd 0 0 0 1",
    },
    "heli": {
        "airplane_landing": " 0.76052475 0.65837479 0.57758057 3 400000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
        "airplane_taxi": "0.76052475 0.65837479 0.57758057 3 50000cd 0.034766696 -0.052357007 -0.99802303 0.97992471",
        "airplane_nav": "0.89626974 0.099898659 0 0 700cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_nav_left": "0.89626974 0.099898659 0 0 700cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_nav_right": "0.020288363 0.73791075 0.36130685 0 7000cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_nav_tail": "0.94730663 0.82278603 0.7230553 0 1500cd -0.077866882 -0.018656421 -0.99678928 0.34202015",
        "airplane_strobe": "3.7129087 -0.07354179 -1.1133618 1 1 1 0 5000cd 0.66745675 0.06932088 0.74141496 0.4617486",
        "airplane_beacon": "1 0 0 0 5000cd 0 0 0 1",
    },
}


def determine_light_params(aircraft_type: str, light_type: str = "") -> str:
    """Determines the paramaters for the given aircraft type

    Args:
        aircraft_type (str): Aircraft type e.g. B733 for Boeing 737-300
        light_type (str): Light type e.g. airplane_landing

    Returns:
        str: A string with the corresponding light parameters for the given aircraft type
    """

    if light_type == "":
        logger.error("The light type is missing!")
        raise ValueError("The light type is missing!")
    if aircraft_type == "":
        logger.error("The aircraft type is missing!")
        raise ValueError("The aircraft type is missing!")

    for key, value in aircrafts.items():
        if aircraft_type in value:
            logging.debug(f"{aircraft_type} found in {key}")
            return light_params[key][light_type]
    else:
        logging.warning(f"{aircraft_type} not found.. Using default light params!")
        return light_params["airliners"][light_type]


def get_light_params_for_aircraft_type(aircraft_type: str) -> dict[str]:
    """Returns the light parameters for the given aircraft type

    Args:
        aircraft_type (str): Aircraft type e.g. B733 for Boeing 737-300

    Returns:
        dict[str]: A dictionary with the corresponding light parameters for the given aircraft type
    """

    for key, value in aircrafts.items():
        if aircraft_type in value:
            logging.debug(f"{aircraft_type} found in {key}")
            return light_params[key]
    else:
        logging.warning(f"{aircraft_type} not found.. Using default light params!")
        return light_params["airliners"]


def main():

    to_check_aircraft = "Socata"
    light_type = "airplane_landing"

    result = determine_light_params(to_check_aircraft, light_type)

    print(f"Light params for {light_type} are: {result}")


if __name__ == "__main__":
    main()
