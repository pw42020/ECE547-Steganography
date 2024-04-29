import logging
import sys
from typing import Final
from pathlib import Path
from enum import Enum, auto

PATH_TO_ASSETS: Final[Path] = Path(__file__).parent.parent.parent / "assets"
sys.path.append(str(PATH_TO_ASSETS))

# pylint: disable=wrong-import-position
from logging_formatter import CustomFormatter

"""configure logging"""

# create log with 'spam_application'
log = logging.getLogger("My_app")
log.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ch.setFormatter(CustomFormatter())

log.addHandler(ch)


class StegoOrNot(Enum):
    """Enum for image object types."""

    NOT_STEGO = auto()
    STEGO = auto()
