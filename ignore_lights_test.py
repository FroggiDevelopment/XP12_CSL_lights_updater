from light_converters.base_converter import convert_airplane_lights

# animation: str = """
# ANIM_begin
#     ANIM_hide	-1.0 0.0	libxplanemp/controls/landing_lites_on
#     #LIGHT_NAMED	airplane_landing	 2.1435    2.3514    0.0077
#     LIGHT_PARAM	airplane_landing_core	 2.1435    2.3514    0.0077	0 0 -1 1 0.4
#     LIGHT_PARAM	airplane_landing_glow	 2.1435    2.3514    0.0077 0 0 -1 1 0.5
#     LIGHT_PARAM	airplane_landing_flare	 2.1435    2.3514    0.0077	0 0 -1 1 1.0
#     LIGHT_PARAM	airplane_landing_sp	 2.1435    2.3514    0.0077	2 2 2.5 1 300 0.7
#     #LIGHT_NAMED	airplane_landing	-2.1430    2.3514    0.0077
#     LIGHT_PARAM	airplane_landing_core	-2.1430    2.3514    0.0077	0 0 -1 1 0.4
#     LIGHT_PARAM	airplane_landing_glow	-2.1430    2.3514    0.0077 0 0 -1 1 0.5
#     LIGHT_PARAM	airplane_landing_flare	-2.1430    2.3514    0.0077	0 0 -1 1 1.0
#     LIGHT_PARAM	airplane_landing_sp	-2.1430    2.3514    0.0077	2 2 2.5 1 300 0.7
# ANIM_end
# """
print("FIRST RUN")
with open("my_new_animation.txt", "r") as f:
    animation = f.read(
    )

light_params: dict[str, str] = {
    "airplane_landing": "0.76052475 0.65837479 0.57758057 3 800000cd 0.034766696 0.052357007 -0.99802303 0.97629601"}

animation = convert_airplane_lights(
    animation, light_params, "airplane_landing")

with open("my_new_animation.txt", "w") as f:
    f.write(animation)

print("SECOND RUN")
with open("my_new_animation.txt", "r") as f:
    another_animation = f.read()

new_animation = convert_airplane_lights(
    animation, light_params, "airplane_landing")

with open("my_new_animation.txt", "w") as f:
    f.write(new_animation)
