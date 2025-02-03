from collections import deque

class Executor:
    def __init__(self):
        self._tasks = deque()

    def add_task(self, task):
        self._tasks.append(task)

    def execute(self):
        self._tasks.popleft().execute()