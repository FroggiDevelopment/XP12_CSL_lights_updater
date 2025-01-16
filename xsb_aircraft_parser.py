from helpers import get_list_of_files
from pathlib import Path

PATH = "X-CSL/C172/"
IGNORE_OBJECTS = ["glass", "prop", "contrail"]

def get_xsb_files(searchpath: str):
    return get_list_of_files(searchpath, "xsb_aircraft.txt")

def parse_xsb_files(xsb_files: list[Path]):
    for xsb_file in xsb_files:
        with open(xsb_file, "r") as xsb_file:
            lines = xsb_file.readlines()
            for line in lines:
                if line.startswith("OBJ8 "):
                    if any (ignore_object in line for ignore_object in IGNORE_OBJECTS):
                        continue
                    print(line)
                
if __name__ == "__main__":
    xsb_files = get_xsb_files(PATH)
    parse_xsb_files(xsb_files)
    