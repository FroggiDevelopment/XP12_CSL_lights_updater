import re
from pathlib import Path

from helpers import get_list_of_files

PATH = "X-CSL/A320"
IGNORE_OBJECTS: list[str] = ["glass", "prop", "contrail", "fan", "rotor"]
ICAO_IDENTIFIERS: list[str] = [
    "MATCHES",
    "ICAO",
    "AIRLINE",
    "LIVERY"]

def get_xsb_files(searchpath: str):
    return get_list_of_files(searchpath, "xsb_aircraft.txt")

def get_path_part_from_line(line: str) -> str:
    """Extracts the path to the aircraft object from the line

    Args:
        line (str): line with xsb aircaft data

    Returns:
        str: string representation of the path
    """
    if not any((_separator := delimiter) in line for delimiter in [":", "/"]):
        print(f"Could not find separator in {line} Can not create path to object file!")

    pathinfo: str = line.split()[3]
    # get rid of packagename, as this is ALWAYS the first part of the pathinfo!
    path_only: str = pathinfo.split(_separator, 1)[1]
    return(path_only)

def parse_xsb_files(xsb_files: list[Path]):
    aircraft_object_files: list[dict[str, str]] = []
    for xsb_file in xsb_files:
        parentdir: Path = xsb_file.parent.absolute()
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
                    if any (iaco_identifier in line for iaco_identifier in ICAO_IDENTIFIERS):
                        icao = line.split()[1]
                        if icao in aircraft_object:
                            print("Alreaddy set!")
                        else:
                            aircraft_object["icao_type"] = icao
                            
                    # Ignore lines with no usefull information
                    if not line.startswith("OBJ8 "):
                        continue
                    if any (ignore_object in line.lower() for ignore_object in IGNORE_OBJECTS):
                        continue
                    
                    #Get the parh to this aircraft object
                        
                        continue
                    path = get_path_part_from_line(line)
                    full_path = str(parentdir) + "/" + path
                    aircraft_object["full_object_path"] = full_path
                    
                aircraft_object_files.append(aircraft_object)
    
        unique_aircraft_objects: list[dict[str, str]] = []
        [unique_aircraft_objects.append(val) for val in aircraft_object_files if val not in unique_aircraft_objects]

        print(unique_aircraft_objects)
        print(f"Aircrafts to convert in {str(parentdir)}: {len(unique_aircraft_objects)}")

                    
def get_aircract_objects(searchpath: str):
    xsb_files = get_xsb_files(searchpath)
    list_of_aircraft_objects = parse_xsb_files(xsb_files)
    return list_of_aircraft_objects
                
if __name__ == "__main__":
    aircraft_objects = get_aircract_objects(PATH)
    # print(aircraft_objects)
    # print(f"Found {len(aircraft_objects)} objects to convert!")