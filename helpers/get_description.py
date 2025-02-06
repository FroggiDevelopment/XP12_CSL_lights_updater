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