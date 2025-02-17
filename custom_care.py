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
from helpers import get_aircraft_objects_from_xsb_file

# from pathlib import Path

def main():
    path: str = "Custom"
    good_aircraft_objects: list[dict[str, str]] = []
    
    light_to_search_for: list[str] = [
        "airplane_landing",
        "airplane_taxi",
        "airplane_nav",
        "airplane_strobe",
        "airplane_beacon",
        # Add more light types here as needed
    ]

    aircraft_objects = get_aircraft_objects_from_xsb_file(path)
    
    for aircraft_object in aircraft_objects:
        with open(aircraft_object["full_object_path"], 'r') as aircraft_object_file:
            content: str = aircraft_object_file.read()
            
            if any(light in content for light in light_to_search_for):
                good_aircraft_objects.append(aircraft_object)
                
    print(f"Found {len(good_aircraft_objects)} objects with light(s) included")   
    
    for good_aircraft_object in good_aircraft_objects:
        print("###################################################")
        print(f"{good_aircraft_object['full_object_path']}")
        print("###################################################")
        with open(good_aircraft_object["full_object_path"]) as good_aircraft_object:
            content_rows = good_aircraft_object.readlines()
            
            for row in content_rows:
                if "LIGHT_PARAM" in row or "LIGHT_NAMED" in row:
                    if any(light in row for light in light_to_search_for):
                        print(row.strip())    
            

if __name__ == '__main__':
    main()