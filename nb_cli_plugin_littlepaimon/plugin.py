from typing import cast


from nb_cli.cli import CLIMainGroup, cli


from .cli import paimon


def main():
    cli_ = cast(CLIMainGroup, cli)
    cli_.add_command(paimon)
    cli_.add_aliases('paimon', ['pm'])