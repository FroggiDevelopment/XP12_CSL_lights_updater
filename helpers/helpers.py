def make_backup(file, backup_extension=".BCK") -> None:
    """Make a backup of the given file

    Arguments: file: string
    """
    backup_file = file.with_suffix(backup_extension)
    if not backup_file.exists():
        backup_file.write_bytes(file.read_bytes())
