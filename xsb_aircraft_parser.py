from helpers import get_list_of_files
from pathlib import Path
from typing import TypedDict

class Aircraftobject(TypedDict):
    icao_type: str
    full_object_path: Path

PATH = "X-CSL"
IGNORE_OBJECTS: list[str] = ["glass", "prop", "contrail", "fan", "rotor"]
ICAO_IDENTIFIERS: list[str] = [
    "MATCHES",
    "ICAO",
    "AIRLINE",
    "LIVERY"]

def get_xsb_files(searchpath: str):
    return get_list_of_files(searchpath, "xsb_aircraft.txt")

# def parse_xsb_files(xsb_files: list[Path]):
#     aircraft_object_files: list[Aircraftobject] = []
    
#     for xsb_file in xsb_files:
#         aircraft_object_path_list: list[Path] = []
#         full_xsb_file_path: Path = xsb_file.parent.absolute()
#         aircraft_object: Aircraftobject = {}
#         with open(xsb_file, "r") as xsb_file:
#             lines = xsb_file.readlines()
#             for line in lines:
#                 if any (iaco_identifier in line for iaco_identifier in ICAO_IDENTIFIERS):
#                         icao = line.split()[1]
#                         if "icao" == aircraft_object:
#                             print("Alreaddy set!")
#                         else:
#                             aircraft_object["icao_type"] = icao
#                 if line.startswith("OBJ8 "):
#                     if any (ignore_object in line.lower() for ignore_object in IGNORE_OBJECTS):
#                         continue
#                     print(line)
#                     aircraft_object_path = Path(full_xsb_file_path, line.split()[3].split("/")[1])
#                     if not aircraft_object_path.exists():
#                         print(f"Aircraft not found for this path: {str(aircraft_object_path)}")
#                         continue
#                     aircraft_object_path_list.append(aircraft_object_path)
#                     aircraft_object["path"] = aircraft_object_path
#         print(aircraft_object)            
#     return list(set(aircraft_object_files))

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
    for xsb_file in xsb_files:
        full_xsb_file_path: Path = xsb_file.parent.absolute()
        with open(xsb_file, "r") as xsb_file:
            lines = xsb_file.readlines()
            for line in lines:
                if not line.startswith("OBJ8 "):
                    continue
                if any (ignore_object in line.lower() for ignore_object in IGNORE_OBJECTS):
                    continue
                path = get_path_part_from_line(line)
                print(Path(full_xsb_file_path, path))
                    
def get_aircract_objects(searchpath: str):
    xsb_files = get_xsb_files(searchpath)
    list_of_aircraft_objects = parse_xsb_files(xsb_files)
    return list_of_aircraft_objects
                
if __name__ == "__main__":
    aircraft_objects = get_aircract_objects(PATH)
    # print(aircraft_objects)
    # print(f"Found {len(aircraft_objects)} objects to convert!")