"""Console script for tetra."""
import click
import sys


@click.command()
def main(args=None):
    """Console script for tetra."""
    click.echo("Replace this message by putting your code into " "tetra.cli.main")
    click.echo("See click documentation at https://click.palletsprojects.com/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
