from ..ml.model import Model

class Task:
    def __init__(self, task_id: int, task_name: str, model: Model):
        self._task_id = task_id
        self._task_name = task_name
        self._model = model

    def get_task_id(self) -> int:
        return self._task_id

    def get_task_name(self) -> str:
        return self._task_name

    def execute(self, input_data: dict) -> dict:
        return self._model.predict(input_data)