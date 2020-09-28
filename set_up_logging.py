import logging
import argparse

def set_up_logging():
    logging_level = logging.WARNING
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--info', action='store_true')
    args = parser.parse_args()
    if args.debug:
        logging_level = logging.DEBUG
    elif args.info:
        logging_level = logging.INFO
    logging.basicConfig(level=logging_level)
