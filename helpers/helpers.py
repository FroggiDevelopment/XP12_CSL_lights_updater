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

log = logging.getLogger("helpers")


def make_backup(
    *,
    files: list[Path],
    stop_on_error: bool = True,
) -> None:
    """Make a backup of the files.

    Arguments: files: string List of files to be backed up.
               stop_on_error: bool Stop on errors or continue. Defaults to True.
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
        log.info(f"BAckup for {file.name} successfully created.")
        continue
    log.info("Backups done!")


def delete_backups(files: list[Path]) -> None:
    """Delete the backup files

    Arguments: files: string
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
    """Delete the files, a genric function to delete all files with a specific suffix

    Arguments: files: string List of files to be deleted.
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

    Arguments: searchpath (Path): The path to the csl location. Is equal to csl_path in config.ini
               filename (str): The name of the file to be searched for.

    Returns:
        list[Path]: The list of files with the given filename.
    """
    files = list(Path(searchpath).rglob(filename))
    if files == []:
        raise NoFilesFoundError(message=f"No {filename} found in {searchpath}!")
    log.debug(f"Found these files while globing: {files}")
    return files


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
