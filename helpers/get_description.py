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
import platform

DESCRIPTION = """
This program can convert XP11 lightparams of CSL aircraft objects to the new XP12 specifications.
Developed for getting landing lights for LifeTraffic.
Works with Bluebell and X-CSL packages, works only with some custom CSL aircraft.

For normal start you don't need any arguments.
But then you \x1b[1;4;31mMUST\x1b[0m specify the csl_path in the config.ini file!
"""

EPILOG = """
\x1b[1;31m!!Attention!!
If you specify a path with -p / --path when processing the objects and you want to undo your changes,
or remove the backup files with -r / --remove-backups, you need the specify the path again!
If you don't and there is a path specified in the config.ini, results may not be what you expected!\x1b[0m

Now you know!\n
"""

DESCRIPTION_WINDOWS = """
This program can convert XP11 lightparams of CSL aircraft objects to the new XP12 specifications.
Developed for getting landing lights for LifeTraffic.
Works with Bluebell and X-CSL packages, works only with some custom CSL aircraft.

For normal start you don't need any arguments.
But then you !!MUST!! specify the csl_path in the config.ini file!
"""

EPILOG_WINDOWS = """
!!ATTENTION!!
If you specify a path with -p / --path when processing the objects and you want to undo your changes,
or remove the backup files with -r / --remove-backups, you need the specify the path again!
If you don't and there is a path specified in the config.ini, results may not be what you expected!\x1b[0m

Now you know!\n
"""

def get_description():
    if platform.system() == "Windows":
        return DESCRIPTION_WINDOWS, EPILOG_WINDOWS
    elif platform.system() == "Linux" or platform.system() == "Darwin":
        return DESCRIPTION, EPILOG
    return "Plain text here"

if __name__ == "__main__":
    description, epilog = get_description()
    print(description)
    print(epilog)