"""
Copyright (C) 2024  Richard Muller

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

from pathlib import Path
from typing import NoReturn
import logging
import sys

log = logging.getLogger("helpers")


def make_backup(
    *,
    files: list,
    stop_on_error: bool = "True",
) -> NoReturn:
    """Make a backup of the files.

    Arguments: files: string List of files to be backed up.
               stop_on_error: bool Stop on errors or continue. Defaults to True.
    """
    for file in files:
        backup_file = file.with_suffix(".BCK")
        if not backup_file.exists():
            try:
                backup_file.write_bytes(file.read_bytes())
            except PermissionError as err:
                if stop_on_error == True:
                    log.error("Stopping on error!", err)
                    sys.exit()
            log.debug(f"Backup for {file} is ready!")
            continue
        log.info(f"Backup already exists for: {file.name}")
    log.info("Backups done!")


def delete_backups(files: list[Path], backup_extension: str) -> NoReturn:
    """Delete the backup files

    Arguments: files: string
    """
    # TODO: Error handling
    log.info("Start of deleting backups!")
    delete_files(files, backup_extension)
    log.info("Backups deleted!")


def recover_from_backup(*, files: list, stop_on_error: bool = False) -> NoReturn:
    """Recover the original files from the backup files

    Args:
        files (list): the 'original' fileslist
        stop_on_error (bool, optional): Stop on any errors or continue. Defaults to False.
    """
    for backup_file in files:
        backup_file = backup_file.with_suffix(".BCK")
        recover_file = backup_file.with_suffix(".obj")
        log.debug(f"Recovery of {backup_file} is started")
        try:
            recover_file.write_bytes(backup_file.read_bytes())
        except PermissionError as err:
            if stop_on_error == True:
                log.error("Stopping on error!", err)
                sys.exit()
            continue
        except FileNotFoundError as notfound:
            if stop_on_error == True:
                log.error("Stopping because backup not found!", notfound)
                sys.exit()
            continue
        backup_file.unlink()
        log.debug(f"Recovery of {recover_file} is done!")
        log.debug(f"Recovering {backup_file}")
    log.info("Recovery done!")


def remove_xpmp2_files(filepath: Path) -> NoReturn:
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


def delete_files(files: list[Path], suffix: str = None):
    """Delete the files, a genric function to delete all files with a specific suffix

    Arguments: files: string List of files to be deleted.
    """
    # TODO: Error handling
    for file in files:
        if suffix is not None:
            file = file.with_suffix(suffix)
        if file.exists():
            log.info(f"Deleting {file}!")
            log.debug(f"Deleting {file}!")
            file.unlink()
