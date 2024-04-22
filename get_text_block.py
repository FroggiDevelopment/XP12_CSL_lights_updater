from pathlib import Path
import re

start_delimiter: str = (
    "ANIM_show 0.500000 2.000000 libxplanemp/controls/landing_lites_on"
)
end_delimiter: str = "ANIM_end"

file_to_open: Path = Path("CSL/BB_Airbus/A306/A306_AAW_test.obj")

print(type(file_to_open))

with open(file_to_open, "r") as file:
    file_content = file.read()

result = re.findall(
    "(?s)(?<=ANIM_show 0.500000 2.000000 libxplanemp/controls/landing_lites_on)(.+?)ANIM_end",
    file_content,
)

for num, item in enumerate(result):
    print(f"{num}. {item}")
