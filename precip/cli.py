"""
Command line entrypoint for working with HPD data.
"""
import argparse
import logging

from precip.enums import StateEnum
from precip.etl import StateETL

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description="HPD Tool")
parser.add_argument(
    "--states",
    default="AZ",
    type=str,
    nargs="*",
    help="The state to perform the action for",
    choices=[v.name for v in StateEnum],
)
parser.add_argument(
    "-v",
    "--verbose",
    default=False,
    action="store_true",
    help="Whether to show debug messages or not",
)
parser.add_argument("command", choices=[])


def run(args):
    """
    Interprets arguements and runs the desired command.
    """
    # Configure logger according to the arguments given
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level)

    try:
        # Convert the requested states into the appropriate enum
        states = [StateEnum._member_map_[s] for s in args.states]
    except KeyError:
        # This shouldn't happen because valid states are checked for by
        # argparse
        logger.error("Invalid US state specified")
        raise

    # If we wanted, we could specify multiple states and perform the
    # desired command for each
    for state in states:
        etl = StateETL(state)
        # Perform user specified action for the ETL
        try:
            getattr(etl, args.command)()
        except AttributeError:
            # This shouldn't happen because of the choice limitation on the
            # command argument
            logger.error("Invalid command specified")
            raise


if __name__ == "__main__":
    parsed_args = parser.parse_args()
    run(parsed_args)
