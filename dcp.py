"""Command line utility for coping of files and folders via python bypassing system call."""
from __future__ import annotations
from hashlib import sha256
from io import DEFAULT_BUFFER_SIZE
from pathlib import Path
from time import perf_counter
from typing import Optional, Callable, BinaryIO, Any

import typer
import humanize

__version__ = "1.0.0"


class Stats:
	"""
	Helper class that counts and formats statistical data with context manager.
	"""

	def __init__(self):
		self.start_time: Optional[float] = None
		self.end_time: Optional[float] = None
		self.file_counter: int = 0
		self.size_counter: int = 0

	@staticmethod
	def _get_time() -> float:
		return perf_counter()

	def __enter__(self) -> Stats:
		self.start_time = Stats._get_time()
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.end_time = Stats._get_time()

	@property
	def time(self) -> str:
		"""
		Format passed time.
		"""
		if self.start_time is None or self.end_time is None:
			raise ValueError('Stats are not recorded yet. Yoy must use context manager before formatting stats.')
		return humanize.precisedelta(self.end_time - self.start_time)

	@property
	def size(self) -> str:
		"""
		Format copied data size.
		"""
		return humanize.naturalsize(self.size_counter, gnu=True)

	@property
	def files(self) -> str:
		"""
		Format copied files count.
		"""
		return humanize.intcomma(self.file_counter)

	@property
	def speed(self) -> str:
		"""
		Format copy speed.
		"""
		if self.start_time is None or self.end_time is None:
			raise ValueError('Stats are not recorded yet. Yoy must use context manager before formatting stats.')
		return humanize.naturalsize(self.size_counter / (self.end_time - self.start_time), gnu=True) + '/s'


def print_version(value: bool):
	"""
	Print version and exit.
	"""
	if value:
		typer.echo(f"Deep copy version: {__version__}")
		raise typer.Exit()


# noinspection PyUnusedLocal
def copy(
		source: Path = typer.Argument(..., exists=True, readable=True, resolve_path=True, help='Path to directory or file to copy from.'),
		destination: Path = typer.Argument(..., writable=True, resolve_path=True, help='Path to directory or file to copy to. In case of copying file to directory it is saved into that directory.'),
		buffer: int = typer.Option(DEFAULT_BUFFER_SIZE, '--buffer', '-b', help='In-memory buffer maximum size for reading and writing files. By default system buffer size is used.'),
		overwrite: Optional[bool] = typer.Option(None, '--overwrite', '-o', help='Whether to overwrite existing files. By default user is prompted about each file.'),
		dry_run: bool = typer.Option(False, '--dry-run', '-d', help='Do not actually perform copy operation.'),
		version: bool = typer.Option(False, "--version", '-v', callback=print_version, is_eager=True, help='Print version and exit.'),
		quiet: bool = typer.Option(False, '--quiet', '-q', help='Do not print anything to stdout, only to stderr.')):
	"""
	Copy file or directory recursively from source location to destination location.
	"""
	try:
		if not quiet:
			typer.echo(f'Copying from {source.absolute()} to {destination.absolute()}')
		stats = Stats()
		with stats:
			if source.is_file():
				if destination.exists() and destination.is_dir():
					destination /= source.name
				copy_file(source, destination, buffer, overwrite, dry_run, stats)
			else:
				copy_directory(source, destination, buffer, overwrite, dry_run, stats)
		if not quiet:
			typer.echo(f'Copied {stats.size} of {stats.files} file(s) in {stats.time} ({stats.speed}).')
	except Exception as error:
		typer.secho(str(error), fg=typer.colors.RED, err=True)
		raise typer.Exit(-1)


def copy_directory(source: Path, destination: Path, buffer_size: int, overwrite: Optional[bool], dry: bool, stats: Stats):
	"""
	Copy all files and directories from source directory to destination one.

	See cli help for details on params.
	"""
	if not source.exists() or not source.is_dir():
		raise ValueError(f'Can not copy directory {source} because it is a file.')
	if destination.exists() and destination.is_file():
		raise ValueError(f'Can not copy directory {source} to file {destination}.')
	with typer.progressbar(list(source.rglob('*'))) as progress:
		for item in progress:
			dst_file = destination / item.relative_to(source)
			if item.is_file():
				copy_file(item, dst_file, buffer_size, overwrite, dry, stats)
			elif not dry:
				dst_file.mkdir(exist_ok=True, parents=True)


def copy_file(source: Path, destination: Path, buffer_size: int, overwrite: Optional[bool], dry: bool, stats: Stats):
	"""
	Copy file to file or directory with the same name.

	See cli help for details on params.
	"""
	if str(source.absolute()) == str(destination.absolute()):
		return
	if not source.exists() or not source.is_file():
		raise ValueError(f'Can not copy from {source} because it is not a file.')
	src_size = source.stat().st_size
	if destination.exists():
		if not destination.is_file():
			raise ValueError(f'Destination location {destination} is not a file.')
		dst_size = destination.stat().st_size
		if src_size == dst_size:
			# hash comparison is simply faster by 34% percents on lots of small files where about 50% are equal
			srs_hash = sha256()
			dst_hash = sha256()
			with open(source, 'rb') as src, open(destination, 'rb') as dst:
				process_stream(src, srs_hash.update, buffer_size)
				process_stream(dst, dst_hash.update, buffer_size)
			if srs_hash.digest() == dst_hash.digest():
				return
		if overwrite is None:
			overwrite = typer.confirm(f'Destination file {destination.absolute()} already exists. Do you want to overwrite it?')
		if not overwrite:
			raise ValueError(f'Destination file {destination.absolute()} already exists.')
	stats.file_counter += 1
	stats.size_counter += src_size
	if dry:
		return
	destination.parent.mkdir(parents=True, exist_ok=True)
	with open(source, 'rb') as src, open(destination, 'wb') as dst:
		process_stream(src, dst.write, buffer_size)


def process_stream(stream: BinaryIO, callback: Callable[[bytes], Any], buffer: int):
	"""
	Process stream by chunks of fixed maximum size with callback.
	"""
	while buf := stream.read(buffer):
		callback(buf)


def main():
	"""
	Entry point.
	"""
	typer.run(copy)


if __name__ == "__main__":
	main()
