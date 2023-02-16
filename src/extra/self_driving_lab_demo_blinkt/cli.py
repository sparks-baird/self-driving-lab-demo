import logging
import os
from glob import glob

import click
from click._compat import get_text_stderr
from click.exceptions import UsageError
from click.utils import echo

from self_driving_lab_demo import __version__
from self_driving_lab_demo.core import _logger, fib, setup_logging


def _show_usage_error(self, file=None):
    if file is None:
        file = get_text_stderr()
    color = None

    echo("Error: %s" % self.format_message(), file=file, color=color)
    if self.ctx is not None:
        color = self.ctx.color
        echo("\n\n" + self.ctx.get_help() + "\n", file=file, color=color)


UsageError.show = _show_usage_error  # type: ignore


def check_save_dir(save_dir):
    if save_dir is None:
        raise UsageError("Please specify a path to a directory to save the PNG files.")


def check_path(path, extension):
    if path is None:
        raise UsageError(
            f"Please specify a path to a {extension} file or "
            f"directory containing {extension} files."
        )


def check_files(path, extension):
    if os.path.isdir(path):
        files = glob(os.path.join(path, f"*.{extension}"))
        if not files:
            raise UsageError(f"No {extension.upper()} files found in directory: {path}")
    elif os.path.isfile(path):
        if not path.endswith(f".{extension}"):
            raise UsageError(f"File must have .{extension} extension: {path}")
        files = [path]

    return files


@click.command("cli")
@click.option("--version", is_flag=True, help="Show version.")
@click.option(
    "--path",
    "-p",
    type=click.Path(
        exists=True,
        dir_okay=True,
        file_okay=True,
        readable=True,
    ),
    help="Input filepath",
)
@click.option(
    "--save-dir",
    "-s",
    type=click.Path(exists=False),
    help="Directory in which to save the output file(s).",
)
@click.option("--encode", "runtype", flag_value="encode", help="Encode values.")
@click.option("--decode", "runtype", flag_value="decode", help="Decode values.")
@click.option("--verbose", "-v", help="Set loglevel to INFO.")
@click.option("--very-verbose", "-vv", help="Set loglevel to INFO.")
@click.option(
    "--fibonacci-input",
    "-n",
    type=int,
    default=3,
    help="integer input (n) to calculate the n-th Fibonnaci number",
)
@click.pass_context
def cli(ctx, version, path, save_dir, runtype, verbose, very_verbose, n):
    """
    self_driving_lab_demo command line interface.
    """
    if version:
        click.echo("self_driving_lab_demo version: {}".format(__version__))
        return
    if verbose:
        setup_logging(loglevel=logging.INFO)
    if very_verbose:
        setup_logging(loglevel=logging.DEBUG)

    _logger.debug("Some message to be displayed when using --very-verbose flag")

    # the core functionality
    fib(n)

    # optionally could read from an input file located at ``path`` and output a file to
    # a ``save_dir``
    path
    save_dir

    click.echo(ctx.get_help())


if __name__ == "__main__":
    cli()
