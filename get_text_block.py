from pathlib import Path
import re

def get_original_object(object_path: Path) -> str:
    with open(object_path, "r") as original_object:
        return original_object.read()
    
def write_new_object(new_object_path: Path, content: str) -> None:
     with open(new_object_path, "w") as file:
        file.write(content)

def build_new_object(object_content: str) -> str:
    start_delimiter: str = ("ANIM_show 0.500000 2.000000 libxplanemp/controls/landing_lites_on")
    end_delimiter: str = "ANIM_end"
    result = re.findall(f"(?s)({start_delimiter})(.+?)({end_delimiter})",object_content)

    string_from_tuple = ""

    for item in result:
        if any( "airplane_taxi" in value for value in item):
            for row in item:
                string_from_tuple += row

    string_with_new_dataref=string_from_tuple.replace("landing_lites_on", "taxi_lites_on")
    new_object_content = object_content.replace(string_from_tuple, string_with_new_dataref)
    return new_object_content

def repair_taxi_lights_dataref():
    original_object_file: Path = Path("CSL/BB_GA/BE20/BE20_BGT_test.obj")
    optimized_object_file: Path = Path("CSL/BB_GA/BE20/BE20_BGT_optimized.obj")
    file_content = get_original_object(original_object_file)

    new_object_content = build_new_object(file_content)
    
    with open(optimized_object_file, "w") as file:
        file.write(new_object_content)
    print("Done!")
        
if __name__ == "__main__":
    repair_taxi_lights_dataref()