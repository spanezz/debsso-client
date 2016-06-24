# coding: utf-8
import sys
import argparse

class Command:
    """
    Base class for all debsso commands
    """
    @property
    def name(self):
        return getattr(self, "NAME", self.__class__.__name__.lower())

    @property
    def description(self):
        return self.__doc__.strip().split("\n", 1)[0].strip()

    def argument_parser(self):
        parser = argparse.ArgumentParser(
            prog="debsso " + self.name,
            description=self.description
        )
        return parser


class Cli:
    """
    Command line interface and execution
    """
    def __init__(self):
        self.commands = []

    def get_usage(self):
        usage = ["%(prog)s <command> [<args>]", "", "Available commands:"]
        cmds = []
        for cmd in self.commands:
            cmds.append((cmd.name, cmd.description))
        name_len = max(len(x[0]) for x in cmds)
        for name, desc in cmds:
            usage.append("  " + name.ljust(name_len + 2) + desc)
        return "\n".join(usage)

    def parse_subcommand_name(self):
        """
        Return the subcommand name used in this invocation, removing it from
        sys.argv.
        """
        for idx, arg in enumerate(sys.argv[1:], start=1):
            if arg == "--": break
            if not arg.startswith("-"):
                sys.argv.pop(idx)
                return arg
        return None

    def get_subcommand(self, name):
        """
        Get the subcommand for this name, or None if not found.
        """
        for cmd in self.commands:
            if cmd.name == name:
                return cmd
        return None

    def argument_parser(self):
        parser = argparse.ArgumentParser(
            description="Command line interface for services behind Debian's Single Sign-On",
            usage=self.get_usage()
        )
        parser.add_argument('command', help='Subcommand to run')
        return parser

    def run(self):
        # Hack around limitations of argparse subcommand handling.
        # In particular, we need to be able to do debsso curl <whatever>
        # and argparse does not support partial parsing only for specific
        # subcommands.
        cmd = self.get_subcommand(self.parse_subcommand_name())
        if cmd is None:
            parser = self.argument_parser()
            args, unparsed = parser.parse_known_args()
            # print(args, unparsed)
        else:
            cmd.run()


