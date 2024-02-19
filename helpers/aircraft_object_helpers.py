LIGHT_JETS = ("B733", "B734", "B737", "B738", "B739", "A318", "A319", "A320", "A321")
HEAVY_JETS = (
    "B717",
    "B744",
    "B74F",
    "B752",
    "B763",
    "B772",
    "B773",
    "B77L",
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
)


def determine_light_params(aircraft_type: str) -> str:
    """Determines the paramaters for the give aircraft type

    Args:
        aircraft_type (str): Aircraft type e.g. B733 for Boeing 737-300

    Returns:
        str: A string with the corresponding light parameters for the given aircraft type
    """
    if aircraft_type in HEAVY_JETS:
        return "0.76052475 0.65837479 0.57758057 3 765000cd 0.034766696 -0.052357007 -0.99802303 0.97992471"
    if aircraft_type in LIGHT_JETS:
        return "0.76052475 0.65837479 0.57758057 3 200000cd 0.034766696 -0.052357007 -0.99802303 0.97992471"
