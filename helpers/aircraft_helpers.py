"""
Copyright (C) 2024  Richard J.M. Muller / Froggi

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

from pathlib import Path
import logging

log = logging.getLogger("aircraft_helpers")


def get_aircraft_objects_from_xsb_file(searchpath: str) -> list[str]:
    """Get the aircraft objects from the xsb file and return the paths as a list.

    Args:
        searchpath (str): Topdirectory from which to search for the xsb_aircraft.txt file

    Returns:
        list[str]: List of paths to the aircraft objects in the searchpath.
    """
    if Path(searchpath).is_dir() == False:
        log.error(f"Path {searchpath} is not a reachable directory!")

    aircraft_desc_files: list[Path] = list(Path(searchpath).rglob("xsb_aircraft.txt"))
    aircraft_object_files: list[str] = []

    # Separator differ between Bluebell and X-CSL, standard is / in this case.
    _seperator: str = "/"

    # Start the search for the aircraft objects in the xsb_aircraft.txt file
    for desc_file in aircraft_desc_files:
        parentdir: Path = desc_file.parent.absolute()

        with open(desc_file, "r") as xsb_aircraft_file:
            for line in xsb_aircraft_file:
                if not line.startswith("OBJ8 SOLID YES"):
                    continue
                list_of_params: list[str] = line.split(" ")
                aircraft_dir_file_info: str = list_of_params[3]

                # Separator differ between Bluebell and X-CSL
                if ":" in aircraft_dir_file_info:
                    package = "xcsl"
                    _seperator = ":"
                elif "/" in aircraft_dir_file_info:
                    package = "bluebell"
                    _seperator: str = "/"

                object_path = None

                # X-CSL has texture info in this line! So the number is greater than 5
                if len(list_of_params) > 5:
                    object_file = aircraft_dir_file_info.split(_seperator)[1]
                    object_path = Path(parentdir, object_file)
                elif package == "bluebell":
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
