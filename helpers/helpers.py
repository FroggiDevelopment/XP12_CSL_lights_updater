from pathlib import Path
from typing import NoReturn
import logging
import sys

log = logging.getLogger(__name__)


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
                    logging.error("Stopping on error!", err)
                    sys.exit()
            logging.debug(f"Backup for {file} is ready!")
            continue
        logging.warning("Backup already exists for:", file)
    print("Backups done!")
    logging.info("Backups done!")


def delete_backups(files: list[Path], backup_extension: str) -> NoReturn:
    """Delete the backup files

    Arguments: files: string
    """
    # TODO: Error handling
    print("Start of deleting backups!")
    logging.info("Start of deleting backups!")
    delete_files(files, backup_extension)
    print("Backups deleted!")
    logging.info("Backups deleted!")


def recover_from_backup(*, files: list, stop_on_error: bool = False) -> NoReturn:
    """Recover the original files from the backup files

    Args:
        files (list): the 'original' fileslist
        stop_on_error (bool, optional): Stop on any errors or continue. Defaults to False.
    """
    for backup_file in files:
        backup_file = backup_file.with_suffix(".BCK")
        recover_file = backup_file.with_suffix(".obj")
        logging.debug(f"Recovery of {backup_file.name} is started")
        try:
            recover_file.write_bytes(backup_file.read_bytes())
        except PermissionError as err:
            if stop_on_error == True:
                logging.error("Stopping on error!", err)
                sys.exit()
            continue
        except FileNotFoundError as notfound:
            if stop_on_error == True:
                logging.error("Stopping because backup not found!", notfound)
                sys.exit()
            continue
        backup_file.unlink()
        logging.debug(f"Recovery of {recover_file} is done!")
    print("Recovery done!")
    logging.info("Recovery done!")


def delete_files(files: list[Path], suffix: str = None):
    """Delete the files, a genric function to delete all files with a specific suffix

    Arguments: files: string List of files to be deleted.
    """
    # TODO: Error handling
    for file in files:
        if suffix is not None:
            file = file.with_suffix(suffix)
        if file.exists():
            file.unlink()
