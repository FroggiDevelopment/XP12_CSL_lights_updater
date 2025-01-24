"""
Copyright (C) 2024  Richard J.M. Muller / Froggi

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
from pathlib import Path

from .custom_exceptions import NoFilesFoundError

from decorators.time_benchmark import time_benchmark

log = logging.getLogger(__name__)

# Add screen handler
screen = logging.StreamHandler()
screen.setLevel(logging.INFO)
screenformatter = logging.Formatter("%(name)-12s: %(levelname)-8s - %(message)s")
screen.setFormatter(screenformatter)

log.addHandler(screen)

def make_backup(
    *,
    files: list[Path],
    stop_on_error: bool = True,
) -> None:
    """ Creates backups of the existing object files

    Args:
        files (list[Path]): List of paths to the objetcfiles
        stop_on_error (bool, optional): To stop on errors or continue. Defaults to True.
    """
    for file in files:
        backup_file = file.with_suffix(".BCK")

        if backup_file.exists():
            log.info(f"Backup already exists for: {file.name}")
            continue
        try:
            backup_file.write_bytes(file.read_bytes())
        except PermissionError as err:
            if stop_on_error is True:
                log.error("Stopping on error!", err)
                sys.exit()
            log.error(f"Backup of {file} failed!", err)
            continue
        except FileNotFoundError as notfound:
            if stop_on_error is True:
                log.error("Stopping because file not found!", notfound)
                sys.exit()
            log.error(f"Backup of {file} failed!", notfound)
            continue
        log.info(f"Backup for {file.name} successfully created.")
        continue
    log.info("Backups done!")


def delete_backups(files: list[Path]) -> None:
    """ Deletes all backups

    Args:
        files (list[Path]): List of paths to the objetcfiles
    """
    log.info("Start of deleting backups!")
    delete_files(files, ".BCK")
    log.info("Backups deleted!")


@time_benchmark
def recover_from_backup(*, files: list[Path], stop_on_error: bool = False) -> None:
    """Recover the original files from the backup files

    Args:
        files (list): the 'original' fileslist
        stop_on_error (bool, optional): Stop on any errors or continue. Defaults to False.
    """

    for file in sorted(files):
        backup_file = file.with_suffix(".BCK")
        recover_file = backup_file.with_suffix(".obj")
        log.debug(f"Recovery of {backup_file} is started")
        if backup_file.is_file() == False:
            log.warning(
                f"{backup_file.name} not found! Should it be there? Skipping this one!"
            )
            files.remove(file)
            continue
        try:
            recover_file.write_bytes(backup_file.read_bytes())
        except PermissionError as err:
            if stop_on_error is True:
                log.error("Stopping on error!", err)
                sys.exit()
            log.error(f"Recovery of {backup_file} failed!", err)
            continue

        backup_file.unlink()
        log.info(f"Recovery of {recover_file} is done!")
    log.info(f"Recovery ready! Recoverd {len(files)} files!")


def remove_xpmp2_files(filepath: str) -> None:
    """Remove the copied object files by LifeTraffic as tehy can and will cache them.
       This is to avoid that changes are not visible with LiveTraffic.

    Args:
        filepath (Path): The path to the csl location. Is equal to csl_path in config.ini

    Returns:
        NoReturn: As it says :-)
    """
    xpmp2_files = list(Path(filepath).rglob("*xpmp2.obj"))
    log.debug(xpmp2_files)
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
        if not file.exists():
            log.warning(f"File {file} does not exist! Deleting not possible!")
            continue
        log.info(f"Deleting {file}!")
        try:
            file.unlink()
        except PermissionError as err:
            log.error("Deleting resulted in error!", err)
        except FileNotFoundError as notfound:
            log.error("Deleting resulted in error!", notfound)


def get_list_of_files(searchpath: str, filename: str) -> list[Path]:
    """Get the list of files with the given filename
    Args:
        searchpath (str): Directory from where to search
        filename (str): The needle, filename to search for._

    Raises:
        NoFilesFoundError: As the name says.

    Returns:
        list[Path]: ist of files with the searchresults for the specified filename
    """

    files = list(Path(searchpath).rglob(filename))
    if files == []:
        raise NoFilesFoundError(message=f"No {filename} found in {searchpath}!")
    log.debug(f"Found these files while globing: {files}")
    return files

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

def tuple_to_string(tuple_to_convert: tuple[str]):
    """Convert a tuple to a string

    Args:
        tuple_to_convert (tuple): The tuple to convert

    Returns:
        str: The converted string
    """
    string_from_tuple: str = ""
    for row in tuple_to_convert:
        string_from_tuple += row
    return str(string_from_tuple)
