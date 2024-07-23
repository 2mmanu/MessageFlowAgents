import threading
from enum import Enum

from confluent_kafka import Consumer, KafkaError, KafkaException, Producer

from agentlink.bus.config import BusSettings
from agentlink.bus.message import FipaAclMessage, FipaAclMessageValidator


class BusType(Enum):
    SYS = "sys"
    KNW = "knw"
    REQ = "req"


class Bus:

    def __init__(self, agent_id, queues, bus_type: BusType, bus_config: BusSettings = BusSettings(), filter=True):
        self.agent_id = agent_id
        self._q_in = queues[0]
        self._q_out = queues[1]
        if bus_type == BusType.KNW:
            self._topic = bus_config.channels.ch_knw_name
            self._name = f"{self.agent_id}k"
        elif bus_type == BusType.REQ:
            self._topic = bus_config.channels.ch_req_name
            self._name = f"{self.agent_id}r"
        elif bus_type == BusType.SYS:
            self._topic = bus_config.channels.ch_sys_name
            self._name = f"{self.agent_id}s"
        self._c_ch = self._consumer(bus_config.channels.dns, self._name)
        self._p_ch = self._producer(bus_config.channels.dns)
        self._filter = filter

    def _producer(self, bootstrap_servers):
        producer_config = {"bootstrap.servers": f"{bootstrap_servers.host}:{bootstrap_servers.port}"}
        return Producer(**producer_config)

    def _consumer(self, bootstrap_servers, group_id):
        consumer_config = {
            "bootstrap.servers": f"{bootstrap_servers.host}:{bootstrap_servers.port}",
            "group.id": group_id,
            "client.id": f"{group_id}-0",
            "auto.offset.reset": "latest",
            # 'debug': 'all',
        }
        return Consumer(**consumer_config)

    def _produce(self):
        while True:
            key, value = self._q_out.get()
            flag, message = FipaAclMessageValidator.validate(value)
            try:
                if not flag:
                    raise ValueError(message)
                else:
                    self._p_ch.produce(self._topic, key=key, value=value.to_json())
                    self._p_ch.flush()
            finally:
                self._q_out.task_done()

    def _consume(self):
        try:
            self._c_ch.subscribe([self._topic])
            while True:
                msg = self._c_ch.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        print("%% %s [%d] reached end at offset %d\n" % (msg.topic(), msg.partition(), msg.offset()))
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    try:
                        # t = msg.topic()
                        # k = msg.key().decode('utf-8')
                        m = msg.value().decode("utf-8")
                        m = FipaAclMessage.from_json(m)
                        if not self._filter or (self._filter and m.get_receiver() in [self.agent_id, "all"]):
                            self._q_in.put(m)
                            self._q_in.join()
                    except:
                        # TODO warning
                        pass
        finally:
            self._c_ch.close()

    def _start_consume(self):
        # TODO scale to number of partition (1 partition = 1 th)
        threading.Thread(target=self._consume, daemon=True, name=f"c_{self._name}").start()

    def _start_produce(self):
        threading.Thread(target=self._produce, daemon=True, name=f"p_{self._name}").start()

    def start(self):
        self._start_consume()
        self._start_produce()
