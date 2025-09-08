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
import logging
import logging.config

import json
import sys

# Setup logging


def init_logging():
    logging_config = "configs/logging.conf"
    with open(logging_config, 'r') as configfile:
        try:
            logger_config = json.load(configfile)
        except FileNotFoundError:
            ("Missing logging.conf file. Stopping now!")
            input("Press any key to continue...")
            sys.exit()
        except json.decoder.JSONDecodeError:
            print(
                "Logging config might be corrupted. Please check the configfile for consistency!", flush=True
            )
            input("Press any key to continue...")
            sys.exit()

    logging.config.dictConfig(logger_config)
