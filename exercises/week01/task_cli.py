import argparse
import json
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Task:
    id: str
    title: str
    done: bool = False


class TaskRepository:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> list[Task]:
        if not self.path.exists():
            return []
        try:
            rows = json.loads(self.path.read_text(encoding="utf-8"))
            return [Task(**row) for row in rows]
        except (json.JSONDecodeError, TypeError) as exc:
            raise ValueError(f"任务文件损坏：{self.path}") from exc

    def save(self, tasks: list[Task]) -> None:
        self.path.write_text(
            json.dumps([asdict(task) for task in tasks], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def update_task(tasks: list[Task], task_id: str, *, delete: bool = False) -> list[Task]:
    for task in tasks:
        if task.id == task_id:
            if delete:
                return [item for item in tasks if item.id != task_id]
            task.done = True
            return tasks
    raise ValueError(f"任务不存在：{task_id}")


def main() -> None:
    parser = argparse.ArgumentParser(description="本地任务管理器")
    parser.add_argument("--file", type=Path, default=Path("tasks.json"))
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add")
    add.add_argument("title")
    commands.add_parser("list")
    for name in ("done", "delete"):
        command = commands.add_parser(name)
        command.add_argument("id")
    args = parser.parse_args()
    repository = TaskRepository(args.file)
    tasks = repository.load()

    if args.command == "add":
        tasks.append(Task(id=str(uuid.uuid4())[:8], title=args.title))
        repository.save(tasks)
    elif args.command == "list":
        for task in tasks:
            print(f"[{'x' if task.done else ' '}] {task.id} {task.title}")
    else:
        repository.save(update_task(tasks, args.id, delete=args.command == "delete"))


if __name__ == "__main__":
    main()
