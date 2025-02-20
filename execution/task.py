from abc import ABC, abstractmethod
from typing import Dict

class Task(ABC):
    """
    Создал абстрактный класс задачи, как пример полиморфизма.
    Теперь можно создавать классы различных задач, которые будут реализовывать одни и те же
    методы, но каждый со своей логикой
    """
    def __init__(self, task_id: int, task_name: str):
        self._task_id = task_id
        self._task_name = task_name

    @property
    def task_id(self) -> int:
        return self._task_id

    @property
    def task_name(self) -> str:
        return self._task_name

    @abstractmethod
    def execute(self, input_data: Dict) -> Dict:
        pass


class ModelTask(Task):
    def __init__(self, task_id: int, task_name: str, model):
        super().__init__(task_id, task_name)
        self._model = model

    def execute(self, input_data: Dict) -> Dict:
        return self._model.predict(input_data)

class DataBaseTask(Task):
    def __init__(self, task_id: int, task_name: str, data: Dict):
        super().__init__(task_id, task_name)
        self._data = data

    def execute(self, input_data: Dict) -> Dict:
        return self._data