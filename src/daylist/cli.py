"""Command-line interface for Daylist."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path
from typing import Any

from daylist.store import default_data_file, load_tasks, save_tasks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="daylist", description="Keep a simple task list offline.")
    parser.add_argument("--file", type=Path, default=default_data_file(), help="path to task data")
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="add a task")
    add.add_argument("title", help="what needs doing")
    add.add_argument("--due", type=date.fromisoformat, metavar="YYYY-MM-DD", help="optional due date")

    listing = commands.add_parser("list", help="show tasks")
    listing.add_argument("--all", action="store_true", help="include completed tasks")

    done = commands.add_parser("done", help="mark a task complete")
    done.add_argument("id", type=int, help="task number")

    remove = commands.add_parser("remove", help="remove a task")
    remove.add_argument("id", type=int, help="task number")
    return parser


def _find_task(tasks: list[dict[str, Any]], task_id: int) -> dict[str, Any] | None:
    return next((task for task in tasks if task.get("id") == task_id), None)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        tasks = load_tasks(args.file)
    except ValueError as exc:
        print(f"daylist: {exc}", file=sys.stderr)
        return 1

    if args.command == "add":
        title = args.title.strip()
        if not title:
            parser.error("task title cannot be empty")
        task_id = max((task["id"] for task in tasks), default=0) + 1
        tasks.append({"id": task_id, "title": title, "due": args.due.isoformat() if args.due else None, "done": False})
        save_tasks(args.file, tasks)
        print(f"Added #{task_id}: {title}")
    elif args.command == "list":
        visible = [task for task in tasks if args.all or not task["done"]]
        if not visible:
            print("No tasks to show.")
        for task in visible:
            status = "x" if task["done"] else " "
            due = f" (due {task['due']})" if task.get("due") else ""
            print(f"[{status}] #{task['id']} {task['title']}{due}")
    elif args.command in {"done", "remove"}:
        task = _find_task(tasks, args.id)
        if task is None:
            print(f"daylist: task #{args.id} does not exist", file=sys.stderr)
            return 1
        if args.command == "done":
            task["done"] = True
            print(f"Completed #{args.id}.")
        else:
            tasks.remove(task)
            print(f"Removed #{args.id}.")
        save_tasks(args.file, tasks)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
