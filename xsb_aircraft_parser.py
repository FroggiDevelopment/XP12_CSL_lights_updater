import re
import logging
from pathlib import Path

from helpers import get_list_of_files

log = logging.getLogger("xsb_aircraft_parser")

PATH = "CSL/BB_Props"
IGNORE_OBJECTS: list[str] = ["glass", "prop", "Contrail", "fan", "rotor", "BLUR"]
ICAO_IDENTIFIERS: list[str] = [
    "MATCHES",
    "ICAO",
    "AIRLINE",
    "LIVERY"]

def get_xsb_files(searchpath: str):
    """Gets a list of xsb_aircraft.txt files

    Args:
        searchpath (str): Path from where to search

    Returns:
        list[str]: The list of found xsb_aircraft.txt files
    """
    return get_list_of_files(searchpath, "xsb_aircraft.txt")

def get_path_to_aircraft_object(line: str) -> str:
    """Extracts the path to the aircraft object from the line

    Args:
        line (str): line with xsb aircaft data

    Returns:
        str: string representation of the path
    """
    if not any((_separator := delimiter) in line for delimiter in [":", "/"]):
        log.error(f"Could not find separator in {line} Can not create path to object file!")
        return "no sep error"
    else:
        pathinfo: str = line.split()[3]
        # get rid of packagename, as this is ALWAYS the first part of the pathinfo!
        path_only: str = pathinfo.split(_separator, 1)[1]
        return(path_only)

def parse_xsb_files(xsb_files: list[Path]):
    """This function parses the xsb_aircraft.txt files and
    creates a list of aircraft objects with icao identifiers and path info

    Args:
        xsb_files (list[Path]): _description_

    Returns:
        _type_: _description_
    """
    aircraft_object_files: list[dict[str, str]] = []
    unique_aircraft_objects: list[dict[str, str]] = []
    for xsb_file in xsb_files:
        parentdir: str = str(xsb_file.parent.absolute())
        with open(xsb_file, "r") as xsb_aircraft_file:
            content: str = xsb_aircraft_file.read()
            aircraft_descriptions: list[str] = re.findall(
                r"(?s)OBJ8_AIRCRAFT.*?(?=OBJ8_AIRCRAFT|$)",
                content,
            )

            for aircraft_description in aircraft_descriptions:
                aircraft_object: dict[str, str] = {}
                
                for line in aircraft_description.split("\n"):
                    # Get ICAO identifier for this aircraft
                    if any (icao_identifier in line for icao_identifier in ICAO_IDENTIFIERS):
                        icao = line.split()[1]
                        if icao in aircraft_object:
                            print(f"ICAO {icao} is already set!")
                            continue
                        else:
                            # print(f"Adding {icao} to aircraft_object, found from {line.split()[0]}")
                            aircraft_object["icao_type"] = icao
                            
                    # Ignore lines with no usefull information
                    if not line.startswith("OBJ8 "):
                        continue
                    if any (ignore_object in line for ignore_object in IGNORE_OBJECTS):
                        continue
                    
                    #Get the path to this aircraft object
                    # print(line)
                    path = get_path_to_aircraft_object(line)
                    full_path = parentdir + "/" + path
                    aircraft_object["full_object_path"] = full_path
                    
                aircraft_object_files.append(aircraft_object)
    
        [unique_aircraft_objects.append(val) for val in aircraft_object_files if val not in unique_aircraft_objects]
    return unique_aircraft_objects

                    
def get_aircraft_objects(searchpath: str):
    xsb_files = get_xsb_files(searchpath)
    list_of_aircraft_objects = parse_xsb_files(xsb_files)
    print(list_of_aircraft_objects)
                
if __name__ == "__main__":
    print("This is a library. Not usabel on its own!")
    get_aircraft_objects("CSL/BB_Props")
