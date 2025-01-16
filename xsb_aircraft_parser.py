from helpers import get_list_of_files
from pathlib import Path

PATH = "X-CSL"
IGNORE_OBJECTS = ["glass", "prop", "contrail", "fan", "rotor"]

def get_xsb_files(searchpath: str):
    return get_list_of_files(searchpath, "xsb_aircraft.txt")

def parse_xsb_files(xsb_files: list[Path]):
    aircraft_object_path_list: list[Path] = []
    for xsb_file in xsb_files:
        full_xsb_file_path: Path = xsb_file.parent.absolute()
        with open(xsb_file, "r") as xsb_file:
            lines = xsb_file.readlines()
            for line in lines:
                if line.startswith("OBJ8 "):
                    if any (ignore_object in line.lower() for ignore_object in IGNORE_OBJECTS):
                        continue
                    aircraft_object_path = Path(full_xsb_file_path, line.split()[3].split(":")[1])
                    if not aircraft_object_path.exists():
                        # print(f"Aircraft not found for this path: {str(aircraft_object_path)}")
                        continue
                    aircraft_object_path_list.append(aircraft_object_path)
                    
    return list(set(aircraft_object_path_list))
                    
def get_aircract_objects(searchpath: str):
    xsb_files = get_xsb_files(searchpath)
    list_of_aircraft_objects = parse_xsb_files(xsb_files)
    print(list_of_aircraft_objects)
                
if __name__ == "__main__":
    get_aircract_objects(PATH)