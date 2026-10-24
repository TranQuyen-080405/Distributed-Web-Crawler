import json

from confluent_kafka import Consumer, Producer


def make_producer(bootstrap: str) -> Producer:
    return Producer({"bootstrap.servers": bootstrap})


def make_consumer(bootstrap: str, group: str, topic: str) -> Consumer:
    consumer = Consumer(
        {
            "bootstrap.servers": bootstrap,
            "group.id": group,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )
    consumer.subscribe([topic])
    return consumer


def publish(producer: Producer, topic: str, payload: dict[str, object], key: str) -> None:
    producer.produce(topic, json.dumps(payload).encode(), key.encode())
    producer.poll(0)


def flush(producer: Producer) -> None:
    pending = producer.flush(10)
    if pending:
        raise RuntimeError(f"{pending} kafka messages were not delivered")
