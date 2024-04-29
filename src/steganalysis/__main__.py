import sys
import argparse
import logging
from .utils import log
from .analyze import enhanced_lsb_matching

parser = argparse.ArgumentParser(
    prog="Steganalysis for Stegosaurus",
    description="Performs steganalysis on images received as input.",
)

parser.add_argument("filename", type=str, help="The path to the image file.")
parser.add_argument(
    "--verbose", action="store_true", help="Enable verbose mode.", default=False
)


if __name__ == "__main__":
    args = parser.parse_args()
    if args.filename == None:
        print("No filename provided.")
        sys.exit(1)
    if args.verbose:
        log.setLevel(logging.DEBUG)
        log.debug("Verbose mode enabled.")

    enhanced_lsb_matching(args.filename)
