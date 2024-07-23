import textwrap

from confluent_kafka import Consumer, KafkaError, KafkaException, Producer


def producer(bootstrap_servers):
    producer_config = {"bootstrap.servers": bootstrap_servers}
    return Producer(**producer_config)


def consumer(bootstrap_servers, group_id):
    consumer_config = {
        "bootstrap.servers": bootstrap_servers,
        "group.id": group_id,
        "auto.offset.reset": "earliest",
        # 'debug': 'all',
    }
    return Consumer(**consumer_config)


def produce(producer, topic, key, value):
    producer.produce(topic, key=key, value=value)
    producer.flush()


def consume(consumer, topics, poll_timeout=1.0):
    # try:
    consumer.subscribe(topics)
    while True:
        msg = consumer.poll(poll_timeout)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                print("%% %s [%d] reached end at offset %d\n" % (msg.topic(), msg.partition(), msg.offset()))
            elif msg.error():
                raise KafkaException(msg.error())
        else:
            return msg.topic(), msg.key().decode("utf-8"), msg.value().decode("utf-8")


# finally:
#     # Close down consumer to commit final offsets.
#     self.consumer.close()


def dump_next_message(topic, group_id="dump"):
    wrapper = textwrap.TextWrapper(width=300, expand_tabs=False, replace_whitespace=False)
    c = consumer(bootstrap_servers="localhost:9092", group_id=group_id)
    _, _, msg = consume(c, [topic])
    return wrapper.fill(msg)
