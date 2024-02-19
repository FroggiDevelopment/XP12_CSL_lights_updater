def make_backup(file) -> None:
    """Make a backup of the given file

    Arguments: file: string
    """
    backup_file = file.with_suffix(".obj.BCK")
    if not backup_file.exists():
        backup_file.write_bytes(file.read_bytes())
