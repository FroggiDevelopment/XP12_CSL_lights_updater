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

import logging
import sys
import json
from pathlib import Path

from .init_logging import init_logging

from .custom_exceptions import NoFilesFoundError

from decorators.time_benchmark import time_benchmark

# Setup logging
init_logging()
log = logging.getLogger(__name__)


def paused_exit() -> None:
    """ Before exiting ask the user to press key. Will help seeing possible messages before the window closes.
    """
    input("Press any key to continue...")
    sys.exit()


def make_backup(
    aircraft_objects: list[dict[str, str]]
) -> None:
    """ Creates backups of the existing object files

    Args:
        files (list[Path]): List of paths to the objetcfiles
    """
    for aircraft_object in aircraft_objects:
        file = Path(aircraft_object["full_object_path"])
        backup_file = file.with_suffix(".BCK")

        if backup_file.exists():
            log.info(f"Backup already exists for: {file}")
            continue
        try:
            backup_file.write_bytes(file.read_bytes())
        except PermissionError as err:
            log.error(f"Backup of {file} failed!", err)
            continue
        except FileNotFoundError as notfound:
            log.error(f"Backup of {file} failed!", notfound)
            continue
        log.info(f"Backup for {file} successfully created.")
        continue
    log.info("Backups done!")


@time_benchmark
def recover_from_backup(aircraft_objects: list[dict[str, str]]) -> None:
    """Recover the original files from the backup files

    Args:
        files (list): the 'original' fileslist
    """

    for aircraft_object in aircraft_objects:
        original_file = Path(aircraft_object["full_object_path"])
        backup_file = original_file.with_suffix(".BCK")

        # log.debug(f"Recovery of {backup_file} is started")
        if backup_file.is_file() is False:
            log.warning(
                f"{backup_file.name} not found! Should it be there? Skipping this one!"
            )
            continue
        try:
            original_file.write_bytes(backup_file.read_bytes())
        except PermissionError as err:
            log.error(f"Recovery of {backup_file} failed!", err)
            continue

        backup_file.unlink()
        log.info(f"Recovery of {original_file} is done!")
        log.debug(f"Recovery of {original_file} succesful!")
    log.info(f"Recovery ready! Recoverd {len(aircraft_objects)} files!")


@time_benchmark
def remove_backups(aircraft_objects: list[dict[str, str]]) -> None:
    """Removes previous backups. This is not reversible!

    Args:
        aircraft_objects (list[dict[str, str]]): A list with all aircraft objects
                                                 including path information
    """
    files_to_remove: list[Path] = []
    log.info("Backups will be removed now! This is PERMANENT!!")
    yes_no = input("Are you sure? yes/No: " or "No")
    if yes_no.lower() == "yes" or yes_no.lower() == "y":
        log.info("Okay! Let's do it....!!")
        for aircraft_object in aircraft_objects:
            files_to_remove.append(Path(aircraft_object["full_object_path"]))
        delete_files(files_to_remove, ".BCK")
        log.info("Backup files removed successfully!")


@time_benchmark
def remove_xpmp2_files(filepath: Path) -> None:
    """Remove the copied object files by LifeTraffic as tehy can and will cache them.
       This is to avoid that changes are not visible with LiveTraffic.

    Args:
        filepath (Path): The path to the csl location. Is equal to csl_path in config.ini

    Returns:
        NoReturn: As it says :-)
    """
    xpmp2_files = list(filepath.rglob("*xpmp2.obj"))
    if len(xpmp2_files) > 0:
        log.debug(xpmp2_files)
    else:
        log.debug("No xpmp2.obj files found.")
    delete_files(files=xpmp2_files)


def delete_files(files: list[Path], suffix: str = ""):
    """Delete files descibed in the list of files

    Args:
        files (list[Path]): List of filepaths to delete
        suffix (str, optional): Suffix if it differs from the suffix in the list of files. Defaults to "".
    """
    for file in files:
        if suffix != "":
            file = file.with_suffix(suffix)
        try:
            file.unlink()
        except PermissionError:
            log.warning(f"Permission denied for deleting {file.name}!")
            continue
        except FileNotFoundError:
            log.warning(f"{file.name} can not be deleted! It doesn't exist.")
            continue


def get_list_of_files(searchpath: Path, filename: str) -> list[Path]:
    """Get the list of files with the given filename
    Args:
        searchpath (str): Directory from where to search
        filename (str): The needle, filename to search for._

    Raises:
        NoFilesFoundError: As the name says.

    Returns:
        list[Path]: ist of files with the searchresults for the specified filename
    """

    files = list(searchpath.rglob(filename))
    if files == []:
        raise NoFilesFoundError(
            message=f"No {filename} found in {searchpath}!")
    # log.debug(f"Found these files while globing: {files}")
    log.debug(f"Found {len(files)} xsb_aircraft.txt files!")
    return files


def is_correct_json_file(json_file: str) -> bool:
    """Check if the json file is correct.

    Args:
        json_file (Path): The path to the json file

    Returns:
        bool: True if correct, False otherwise
    """
    try:
        with open(json_file, "r") as aircrafts_definitions:
            json.load(aircrafts_definitions)
    except FileNotFoundError:
        log.error(f"Missing {json_file} file. Stopping now!")
        return False
    except json.decoder.JSONDecodeError:
        log.error(
            f"{json_file} may be corrupted. Please check the file for consistency!"
        )
        return False

    return True


def filepath_is_valid(filepath: Path) -> bool:
    """Check if the filepath given is valid.

    Args:
        filepath (Path): Path to specific file

    Returns:
        bool: True if valid, False otherwise
    """
    result = True
    if (filepath.exists() is False):
        result = False

    return result


def copy_new_to_old(aircraft_objects: list[dict[str, str]], TEMP_FILE_SUFFIX: str) -> None:
    """Copy the new created files over the original files
       Delete the new files.
    """
    log.info("Start copying processed files to original file!")
    for aircraft_object in aircraft_objects:
        destination_file = Path(
            aircraft_object["full_object_path"]).with_suffix(".obj")
        temp_object_file = Path(
            aircraft_object["full_object_path"]).with_suffix(TEMP_FILE_SUFFIX)

        try:
            destination_file.write_bytes(temp_object_file.read_bytes())
        except PermissionError as err:
            log.error("Stopping on error!", err)
            paused_exit()
            continue
        except FileNotFoundError as err:
            log.error(f"File could not be copied! See: {err}")
            continue
        try:
            temp_object_file.unlink()
        except PermissionError as err:
            log.error(f"{temp_object_file.name} can not be deleted!", err)
            continue
        log.info(
            f"Copying {temp_object_file.name} to {aircraft_object['full_object_path']} file done.")
