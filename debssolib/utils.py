import argparse
import logging
import sys


class Fail(Exception):
    pass


class Command:
    @classmethod
    def add_parser(cls, subparsers):
        doc = [line.strip() for line in cls.__doc__.splitlines()]
        sp = subparsers.add_parser(cls.__name__.lower(), help=" ".join(doc).strip())
        sp.set_defaults(cls=cls)
        return sp


class Cli:
    def __init__(self, *args, **kw):
        self.parser = argparse.ArgumentParser(*args, **kw)
        self.parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
        self.parser.add_argument("--debug", action="store_true", help="Debug output")
        self.subparsers = self.parser.add_subparsers()

    def add_command(self, cls):
        cls.add_parser(self.subparsers)

    def main(self):
        args = self.parser.parse_args()

        # Setup logging
        FORMAT = "%(levelname)s %(message)s"
        if args.debug:
            logging.basicConfig(level=logging.DEBUG, stream=sys.stderr, format=FORMAT)
        elif args.verbose:
            logging.basicConfig(level=logging.INFO, stream=sys.stderr, format=FORMAT)
        else:
            logging.basicConfig(level=logging.WARN, stream=sys.stderr, format=FORMAT)

        try:
            args.cls().run(args)
        except Fail as e:
            print(e, file=sys.stderr)
            sys.exit(1)

        sys.exit(0)
