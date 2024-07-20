from confluent_kafka import Producer, Consumer, KafkaException, KafkaError
from bus.blackboard import Blackboard

class Bus:

    _REQ_CH_TOPIC = "req-channel"
    _KNW_CH_TOPIC = "knw-channel"
    _SYS_CH_TOPIC = "sys-channel"

    def __init__(self, bootstrap_servers, group_id, agent_id):
        self._c_req_ch = self._consumer(bootstrap_servers,f"req-ch-{group_id}")
        self._c_knw_ch = self._consumer(bootstrap_servers,f"knw-ch-{group_id}")
        self._c_sys_ch = self._consumer(bootstrap_servers,f"sys-ch-{group_id}")
        self._p_req_ch = self._producer(bootstrap_servers)
        self._p_knw_ch = self._producer(bootstrap_servers)
        self._p_sys_ch = self._producer(bootstrap_servers)
        self._blackboard = Blackboard()
        self._agent_id = agent_id
        self._hello_word_message()


    def _producer(self,bootstrap_servers):
        producer_config = {
            'bootstrap.servers': bootstrap_servers
        }
        return Producer(**producer_config)
    
    def _consumer(self,bootstrap_servers,group_id):
        consumer_config = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
            # 'debug': 'all',
        }
        return Consumer(**consumer_config)

    @staticmethod
    def _produce(producer, topic, key, value):
        producer.produce(topic, key=key, value=value)
        producer.flush()

    @staticmethod
    def _consume(consumer, topics, poll_timeout=1.0):
        # try:
            consumer.subscribe(topics)
            while True:
                msg = consumer.poll(poll_timeout)
                if msg is None: continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        print('%% %s [%d] reached end at offset %d\n' %
                                        (msg.topic(), msg.partition(), msg.offset()))
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    return msg.topic(), msg.key().decode('utf-8'), msg.value().decode('utf-8')
        # finally:
        #     # Close down consumer to commit final offsets.
        #     self.consumer.close()

    def consume_req_ch(self,fn):
        return self._consume(self.consume_req_ch, [self._REQ_CH_TOPIC], fn, poll_timeout=1.0)
    
    def consume_knw_ch(self,fn):
        return self._consume(self.consume_knw_ch, [self._KNW_CH_TOPIC], fn, poll_timeout=1.0)

    def consume_sys_ch(self,fn):
        return self._consume(self.consume_sys_ch, [self._SYS_CH_TOPIC], fn, poll_timeout=1.0)

    def produce_req_ch(self,key, value):
        self._p_req_ch.produce(self._REQ_CH_TOPIC, key=key, value=value)

    def produce_knw_ch(self,key, value):
        self._p_knw_ch.produce(self._KNW_CH_TOPIC, key=key, value=value)

    def produce_sys_ch(self,key, value):
        self._p_sys_ch.produce(self._SYS_CH_TOPIC, key=key, value=value)

    def _informative_msg(self,content, ontology):
        msg = f"""
        (inform
            :performative "inform"
            :sender (agent-identifier :name {self._agent_id})
            :receiver (set (agent-identifier :name :all))
            :content "{content}"
            :language English
            :ontology {ontology}
        )
        """
        return msg

    def _hello_word_message(self):
        self.produce_sys_ch("FIPA-ACL",self._informative_msg(f"New agent available: {self._agent_id}","AgentAvailability"))
        
    def write(self, address, data):
        self._blackboard.write(address, data)
        self.produce_sys_ch("FIPA-ACL",self._informative_msg(f"Data written to {address} by {self._agent_id}","Notification"))

    def read(self, address):
        data = self._blackboard.read(address)
        self.produce_sys_ch("FIPA-ACL",self._informative_msg(f"Data accessed at {address} by {self._agent_id}","Notification"))
        return data
