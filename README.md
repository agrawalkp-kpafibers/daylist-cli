# Daylist

A small, offline task list for the terminal. It uses only Python's standard library at runtime and keeps tasks in a JSON file on your computer.

## Requirements

Python 3.10 or newer.

## Install

From this project folder:

```bash
python -m pip install -e .
```

## Use

```bash
daylist add "Pay rent" --due 2026-11-05
daylist add "Read a book"
daylist list
daylist done 1
daylist list --all
daylist remove 2
```

If Windows blocks the installed `daylist` launcher, use `python -m daylist` in place of `daylist` in these examples.

Tasks are saved at `~/.daylist/tasks.json`. To use a different file, pass `--file path/to/tasks.json` before the command, or set the `DAYLIST_DATA_FILE` environment variable.

## Run tests

```bash
python -m unittest discover -s tests -v
```

GitHub Actions runs the tests on Python 3.10 and 3.13 for every push and pull request.
