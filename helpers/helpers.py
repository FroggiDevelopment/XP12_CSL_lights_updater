from pathlib import Path
from typing import NoReturn
import logging
import sys

log = logging.getLogger(__name__)


def make_backup(
    *,
    files: list,
    backup_extension: str,
    stop_on_error: bool = "True",
    debug: bool = False,
) -> NoReturn:
    """Make a backup of the given file

    Arguments: files: string
    """
    for file in files:
        backup_file = file.with_suffix(backup_extension)
        if not backup_file.exists():
            try:
                backup_file.write_bytes(file.read_bytes())
            except PermissionError as err:
                if stop_on_error == True:
                    logging.debug("Stopping on error!", err)
                    sys.exit()
            if debug == True:
                logging.debug(f"Backup for {file} is ready!")
            continue
        if debug == True:
            logging.debug("Backup already exists for:", file)
    print("Backups done!")
    debug.info("Backups done!")


def delete_backups(files: list[Path], backup_extension: str):
    delete_files(files, backup_extension)


def recover_from_backup(
    *, files: list, backup_extension: str, stop_on_error: bool = False
) -> NoReturn:

    for backup_file in files:
        backup_file = backup_file.with_suffix(".BCK")
        recover_file = backup_file.with_suffix(".obj")
        try:
            recover_file.write_bytes(backup_file.read_bytes())
        except PermissionError as err:
            if stop_on_error == True:
                logging.debug("Stopping on error!", err)
                sys.exit()
            continue
        except FileNotFoundError as notfound:
            if stop_on_error == True:
                logging.debug("Stopping because backup not found!", notfound)
                sys.exit()
            continue
        backup_file.unlink()
        print(f"Recovery of {backup_file} is done!")
        logging.debug(f"Recovery of {recover_file} is done!")
    print("Recovery done!")
    logging.info("Recovery done!")


def delete_files(files: list[Path], suffix: str = None):
    for file in files:
        if suffix is not None:
            file = file.with_suffix(suffix)
        if file.exists():
            file.unlink()
