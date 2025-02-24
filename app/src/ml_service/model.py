import json
import pika
from config import get_connection_params
from transformers import T5Tokenizer, T5ForConditionalGeneration
from functools import partial
from threading import Thread

class Model:
    def __init__(self, model_id: int, model_name: str, tokenizer_path: str, model_path: str):
        self._model_id = model_id
        self._model_name = model_name
        self.tokenizer = T5Tokenizer.from_pretrained(tokenizer_path)
        self.model = T5ForConditionalGeneration.from_pretrained(model_path)

    @property
    def get_model_id(self) -> int:
        return self._model_id

    @property
    def get_model_name(self) -> str:
        return self._model_name

    def predict(self, ch, method, properties, body):
        # ИИ делает брр-брр
        try:
            data = json.loads(body)
            prompt = data['prompt']

            input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids
            outputs = self.model.generate(input_ids, max_length=200, do_sample=True, top_k=5, top_p=0.9)
            answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            task = {
                "id": data["id"],
                "prediction": answer,
            }
            ch.basic_publish(
                exchange='',
                routing_key="result_ml_task_queue",
                body=json.dumps(task),
                properties=properties,
            )

            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(e)

model = Model(1, "Humorist", "google/flan-t5-base", "google/flan-t5-base")

with pika.BlockingConnection(get_connection_params()) as connection:
    with connection.channel() as channel:
        try:
            channel.queue_declare(queue="ml_task_queue", durable=True)
            channel.queue_declare(queue="result_ml_task_queue", durable=True)

            channel.basic_qos(prefetch_count=1)
            threads = []
            channel.basic_consume(queue="ml_task_queue", on_message_callback=model.predict)
        except Exception as e:
            print(e)

        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()

        for thread in threads:
            thread.join()