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
    content = file.readlines()

pattern = r"(?s)I.*?(?=ANIM_begin|$)"
split_pattern = r"(?=ANIM_begin)"

matches = re.split(split_pattern, content, maxsplit=1)

if matches:
    print(len(matches))
    print(matches[0])
    print(matches[1])
