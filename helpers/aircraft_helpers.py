from pathlib import Path
import logging

log = logging.getLogger(__name__)


def get_aircraft_objects_from_xsb_file(
    searchpath: str, is_xcsl: bool = False
) -> list[str]:
    """Get the aircraft objects from the xsb file and return the paths as a list.

    Args:
        searchpath (str): Topdirectory from which to search for the xsb_aircraft.txt file
        is_xcsl (bool, optional): Is it a X-CSB package? Defaults to False.

    Returns:
        list[str]: List of paths to the aircraft objects in the searchpath.
    """
    if Path(searchpath).is_dir() == False:
        print(f"Path {searchpath} is not a reachable directory!")
        log.error(f"Path {searchpath} is not a reachable directory!")

    aircraft_desc_files: list[Path] = list(Path(searchpath).rglob("xsb_aircraft.txt"))
    aircraft_object_files: list[str] = []

    # Separator differ between Bluebell and X-CSL
    _seperator: str = "/"
    if is_xcsl == True:
        _seperator = ":"

    # Start the search for the aircraft objects in the xsb_aircraft.txt file
    for desc_file in aircraft_desc_files:
        parentdir: Path = desc_file.parent.absolute()

        with open(desc_file, "r") as xsb_aircraft_file:
            for line in xsb_aircraft_file:
                if not line.startswith("OBJ8 SOLID YES"):
                    continue
                list_of_params: list[str] = line.split(" ")
                aircraft_dir_file_info: str = list_of_params[3]
                object_path = None
                if len(list_of_params) > 5:  # X-CSL has texture info in this line!
                    object_file = aircraft_dir_file_info.split(_seperator)[1]
                    object_path = Path(parentdir, object_file)
                elif is_xcsl == False:
                    object_file = aircraft_dir_file_info.split(_seperator, 1)[1].rstrip(
                        "\n"
                    )
                    object_path = Path(parentdir, object_file)
                if object_path is not None and object_path not in aircraft_object_files:
                    aircraft_object_files.append(object_path)
    return aircraft_object_files


def main():
    files = get_aircraft_objects_from_xsb_file("CSL", is_xcsl=False)
    print(files)


if __name__ == "__main__":
    main()
