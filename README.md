# dcp

*Deep copy* is a command line utility for coping files and folders via python bypassing system call.

# Features

* Copies file to file, file to folder, folder to folder.
* Records files count, size, time and speed.
* Performs smart copying without equal files overwrite.
* Support dry runs (without real copying).
* Supports overwrite prompting for each file.
* Copies empty folders.

# Usage

Output from `dcp --help`:

```bash
Usage: dcp.py [OPTIONS] SOURCE DESTINATION

  Copy file or directory recursively from source location to destination
  location.

Arguments:
  SOURCE       Path to directory or file to copy from.  [required]
  DESTINATION  Path to directory or file to copy to. In case of copying file
               to directory it is saved into that directory.  [required]


Options:
  -b, --buffer INTEGER  In-memory buffer maximum size for reading and writing
                        files. By default system buffer size is used.
                        [default: <system value is printed>]

  -o, --overwrite       Whether to overwrite existing files. By default user
                        is prompted about each file.

  -d, --dry-run         Do not actually perform copy operation.  [default:
                        False]

  -v, --version         Print version and exit.  [default: False]
  -q, --quiet           Do not print anything to stdout, only to stderr.
                        [default: False]

  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.

  --help                Show this message and exit.

```

# Why another tool?

Because I sometimes get [Destination Path Too Long](https://answers.microsoft.com/en-us/windows/forum/windows_10-desktop/destination-path-too-long/22ee2a6a-e277-4edc-a4b9-7874737105ef) error when try to copy files from unix disks. Actually this is Explorer's issue that can not be fixed since 2016.

---

Issue tracker at [github](https://github.com/baterflyrity/dcp/issues).

Built with nice CLI framework [Typer](https://typer.tiangolo.com/).