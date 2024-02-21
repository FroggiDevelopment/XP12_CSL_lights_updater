LIGHT_NEEDLES = [
    "airplane_landing",
    "airplane_taxi",
    "airplane_nav_left",
    "airplane_nav_right",
    "airplane_nav_tail",
    "airplane_strobe",
    "airplane_beacon",
]

text = """
ANIM_begin
ANIM_hide -1.000000 0.400000 libxplanemp/controls/strobe_lites_on
ANIM_show 0.500000 2.000000 libxplanemp/controls/strobe_lites_on
LIGHT_PARAM airplane_strobe_test -30.107676 2.573810 8.573019
LIGHT_PARAM airplane_strobe_test 29.994944 2.525130 8.613919
ANIM_begin
"""

if any(light_type in text for light_type in LIGHT_NEEDLES):
    if any(light in text for light in LIGHT_NEEDLES):
        print("Light found")
else:
    print("not found")
