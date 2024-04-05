class NoFilesFoundError(Exception):
    """Exception raised when no files are found"""

    def __init__(self, message: str = "No files found!") -> None:
        self.message = message
        super().__init__(self.message)
