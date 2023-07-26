from typing import cast

from .cli import paimon

from nb_cli.cli import cli, CLIMainGroup


def main():
    cli_ = cast(CLIMainGroup, cli)
    cli_.add_command(paimon)
    cli_.add_aliases("paimon", ["pm"])
