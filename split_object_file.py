import re

objectfile = "/media/froggi/X-Plane-Addons/DEV_Tools/Lights_Updater/Bluebell_Lights_Updater/X-CSL/A319/A319fCFM.obj"

teststring = """
I
800
jkfjskhjkhfdkj
sdahgdshghghjsda
hdsahgjhgdsajhsda
TRIS 8096 1289
ANIM_begin
    ANIM_trans	   6.4140    2.2783   -2.4989	   6.4140    2.2783   -2.4989	0 0	no_ref
    ANIM_rotate_begin	   0.5704   -0.8213    0.0128	libxplanemp/controls/thrust_ratio
        ANIM_rotate_key	0	  0.00
        ANIM_rotate_key	1.0	  0.00
        ANIM_rotate_key	-1.0	 65.00
    ANIM_rotate_end
    # engR_revR_top
    ATTR_shiny_rat 1.0
    TRIS	8931 33
    # engR_revR_top
    ATTR_shiny_rat 0.0
    TRIS	8964 57
ANIM_end
"""

with open(objectfile, "r") as file:
    content = file.read()
object_file_content = ""
split_pattern = r"(?=ANIM_begin)"

matches = re.split(split_pattern, content, maxsplit=1)
print(type(matches))
exit()
if matches:
    new_animations: str = ""
    for line_no, line in enumerate(matches[1].split("\n")):
        # print(f"{line_no}. {line}")
        if "LIGHT_NAMED" in line:
            line = line.replace("LIGHT_NAMED", "LIGHT_PARAM")
            print(line)
        if "airplane_beacon_rotate" in line:
            print(line)
        new_animations += line+"\n"

    object_file_content = matches[0] + new_animations

if object_file_content != "":
    print(object_file_content)
    with open("aircraft.obj", "w") as file:
        file.write(object_file_content)
