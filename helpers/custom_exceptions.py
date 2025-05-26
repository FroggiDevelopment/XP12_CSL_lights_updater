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


class NoFilesFoundError(Exception):
    """Exception raised when no files are found"""

    def __init__(self, message: str = "No files found!") -> None:
        self.message = message
        super().__init__(self.message)


class NoAnimationFoundError(Exception):
    """Exception raised when no animations are found"""

    def __init__(self, message: str = "This file contains no animation section!") -> None:
        self.message = message
        super().__init__(self.message)


class WrongAnimationTypeError(Exception):
    """Exception raised when no animations are found"""

    def __init__(self, message: str = "This file contains the wrong type of animation section!") -> None:
        self.message = message
        super().__init__(self.message)
