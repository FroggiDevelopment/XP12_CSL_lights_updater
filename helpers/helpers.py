from pathlib import Path


def make_backup(files: Path, backup_extension) -> None:
    """Make a backup of the given file

    Arguments: files: string
    """
    for file in files:
        backup_file = file.with_suffix(backup_extension)
        if not backup_file.exists():
            backup_file.write_bytes(file.read_bytes())
        print("Backup already exists for:", file)
