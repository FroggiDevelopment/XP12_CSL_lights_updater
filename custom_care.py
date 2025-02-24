"""
Copyright (C) 2025  Richard J.M. Muller / Froggi

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>
"""
import re
import sys
from helpers import get_aircraft_objects_from_xsb_file
from helpers.aircraft_light_params import get_light_params_for_aircraft_type
from helpers import add_lateral_position_to_lights

WANTED_LIGHTS: list[str] = [
    " airplane_landing",
    " airplane_taxi",
    " airplane_nav",
    " airplane_nav_left",
    " airplane_nav_right",
    " airplane_nav_tail",
    " airplane_strobe",
    " airplane_strobe_tail",
    " airplane_beacon",
    " airplane_beacon_rotate",
    " airplane_beacon_strobe",
    # Add more light types here as needed
]


def get_aircraft_objects_with_lights(aircraft_objects: list[dict[str, str]]) -> list[dict[str, str]]:
    good_aircraft_objects: list[dict[str, str]] = []
    for aircraft_object in aircraft_objects:
        with open(aircraft_object["full_object_path"], 'r') as aircraft_object_file:
            content: str = aircraft_object_file.read()

            if any(light in content for light in WANTED_LIGHTS):
                good_aircraft_objects.append(aircraft_object)
    return good_aircraft_objects


def main():
    path: str = "Custom/Diamond_DA62"

    aircraft_objects = get_aircraft_objects_from_xsb_file(path)
    unique_aircraft_lights: list[dict[str, str]] = []

    list_of_aircraft_with_lights: list[dict[str, str]] = []

    for good_aircraft_object in get_aircraft_objects_with_lights(aircraft_objects):
        light_params: dict[str, str] = get_light_params_for_aircraft_type(
            str(good_aircraft_object["icao_type"])
        )

        print("###################################################")
        print(f"{good_aircraft_object['full_object_path']}")
        print("###################################################")
        with open(good_aircraft_object["full_object_path"]) as aircraft_object:
            content_lines = aircraft_object.readlines()

            for line in content_lines:
                line = re.sub("#.* L", "", line)
                line = " ".join(line.split())
                if "airplane_nav" in line or "airplane_strobe" in line:
                    line = add_lateral_position_to_lights(line)
                if "LIGHT_PARAM" in line or "LIGHT_NAMED" in line:
                    print(line)
                    for light in WANTED_LIGHTS:
                        if light in line:
                            coordinates = " ".join(line.split()[2:5])
                            list_of_aircraft_with_lights.append(
                                {"light_type": light, "lightcoordinates": coordinates})

        [unique_aircraft_lights.append(
            val) for val in list_of_aircraft_with_lights if val not in unique_aircraft_lights]
        for aircraft_lights in unique_aircraft_lights:
            print(aircraft_lights)


if __name__ == '__main__':
    main()
    sys.exit()
