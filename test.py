LIGHT_NEEDLES = [
    "airplane_landing",
    "airplane_taxi",
    "airplane_nav_left",
    "airplane_nav_right",
    "airplane_nav_tail",
    "airplane_strobe",
    "airplane_beacon",
]

text = "testtest testtest"

if any(light_type in text for light_type in LIGHT_NEEDLES):
    print("aloha")
else:
    print("not found")
