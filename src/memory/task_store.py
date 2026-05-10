_tasks = []


def save_tasks(tasks: list):
    global _tasks
    _tasks = list(tasks)


def get_tasks() -> list:
    return _tasks


def clear_tasks():
    global _tasks
    _tasks = []


def append_task(task: dict):
    _tasks.append(task)


def has_tasks() -> bool:
    return len(_tasks) > 0
