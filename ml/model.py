from typing import Union

import numpy as np
import pandas as pd

class Model:
    def __init__(self, model_id: int, model_name: str):
        self._model_id = model_id
        self._model_name = model_name

    @property
    def get_model_id(self) -> int:
        return self._model_id

    @property
    def get_model_name(self) -> str:
        return self._model_name

    def predict(self, input_data: Union[np.array, pd.DataFrame, dict]) -> dict:
        # ИИ делает брр-брр
        return {"prediction": "some outputs of the model"}