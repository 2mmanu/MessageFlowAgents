import threading
from confluent_kafka import Producer, Consumer, KafkaException, KafkaError


class Bus:

    def __init__(self, queues, topic, bootstrap_servers, group_id):
        self._q_in = queues[0]
        self._q_out = queues[1]
        self._topic = topic
        self._c_ch = self._consumer(bootstrap_servers,group_id)
        self._p_ch = self._producer(bootstrap_servers)

    def _producer(self,bootstrap_servers):
        producer_config = {
            'bootstrap.servers': bootstrap_servers
        }
        return Producer(**producer_config)
    
    def _consumer(self,bootstrap_servers,group_id):
        consumer_config = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'client.id': f"{group_id}-0",
            'auto.offset.reset': 'earliest',
            # 'debug': 'all',
        }
        return Consumer(**consumer_config)

    def _produce(self):
        while True:
            key, value = self._q_out.get()
            self._p_ch.produce(self._topic, key=key, value=value)
            self._p_ch.flush()
            self._q_out.task_done()

    def _consume(self):
        try:
            self._c_ch.subscribe([self._topic])
            while True:
                msg = self._c_ch.poll(1.0)
                if msg is None: continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        print('%% %s [%d] reached end at offset %d\n' %
                                        (msg.topic(), msg.partition(), msg.offset()))
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    # TODO Filter messages only for the specified agent_id (for sys + all)
                    self._q_in.put((msg.topic(), msg.key().decode('utf-8'), msg.value().decode('utf-8')))
        finally:
            self._c_ch.close()

    def _start_consume(self):
        # TODO scale to number of partition (1 partition = 1 th)
        threading.Thread(target=self._consume, daemon=True).start()
    
    def _start_produce(self):
        threading.Thread(target=self._produce, daemon=True).start()

    def start(self):
        self._start_consume()
        self._start_produce()
