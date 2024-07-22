import uuid
import queue
from bus.core import Bus
from bus.queue import QueueManager
from bus.blackboard import Blackboard
from bus.message import AgentIdentifier, Receiver, FipaAclMessage

class Agent:

    _REQ_CH_TOPIC = "req-channel"
    _KNW_CH_TOPIC = "knw-channel"
    _SYS_CH_TOPIC = "sys-channel"

    def __init__(self, agent_id=None, topics=None):
        
        if not agent_id:
            agent_id = uuid.uuid4().hex[:8]
        self.agent_id = agent_id
        self.topics = topics
        
        self._blackboard = Blackboard()
        
        self._qm = QueueManager()
        self._qm.create_queues("q-req")
        self._qm.create_queues("q-knw")
        self._qm.create_queues("q-sys")
        
        self._bus_req = Bus(
            self.agent_id,
            self._qm.get_queues("q-req"),
            self._REQ_CH_TOPIC,
            bootstrap_servers='localhost:9092',
            group_id=f"{self.agent_id}r",
        )
        self._bus_knw = Bus(
            self.agent_id,
            self._qm.get_queues("q-knw"),
            self._KNW_CH_TOPIC,
            bootstrap_servers='localhost:9092',
            group_id=f"{self.agent_id}k",
        )
        self._bus_sys = Bus(
            self.agent_id,
            self._qm.get_queues("q-sys"),
            self._SYS_CH_TOPIC,
            bootstrap_servers='localhost:9092',
            group_id=f"{self.agent_id}s",
        )
        self._bus_req.start()
        self._bus_knw.start()
        self._bus_sys.start()
        self._hello_word_message()        
    
    def _send_msg(self,q_name,key,msg):
        q_out = self._qm.get_queue(name=q_name,direction="out")
        q_out.put((key,msg))
        q_out.join()
    
    def _receive_msg(self,q_name):
        q_in = self._qm.get_queue(name=q_name,direction="in")
        message = q_in.get()
        q_in.task_done()
        return message
    
    def _hello_word_message(self):
        message = FipaAclMessage(
            performative = "inform",
            sender = AgentIdentifier(name=self.agent_id),
            receiver = Receiver(),
            content = f"The agent {self.agent_id} is now available. You can ask about the following topics: {self.topics}",
            language = "English",
            ontology = "agent-availability"
        )
        self._send_msg(q_name="q-sys",key="FIPA-ACL",msg=message)
    
    def write(self, address, data, receiver_id=None):
        self._blackboard.write(address, data)
        message = FipaAclMessage(
            performative="inform",
            sender = AgentIdentifier(name=self.agent_id),
            receiver = Receiver() if receiver_id is None else Receiver([AgentIdentifier(name=receiver_id)]),
            content = f"Data written to {address} by {self.agent_id}",
            language = "English",
            ontology = "data-availability"
        )
        self._send_msg(q_name="q-sys",key="FIPA-ACL",msg=message)

    def read(self, address, receiver_id=None):
        data = self._blackboard.read(address)
        message = FipaAclMessage(
            performative="inform",
            sender = AgentIdentifier(name=self.agent_id),
            receiver = Receiver() if receiver_id is None else Receiver([AgentIdentifier(name=receiver_id)]),
            content = f"Data accessed at {address} by {self.agent_id}",
            language = "English",
            ontology = "data-access"
        )
        self._send_msg(q_name="q-sys",key="FIPA-ACL",msg=message)
        return data
    
    def get_sys_info(self):
        message = self._receive_msg("q-sys")
        return message.to_dict()
    
    def ask_kb(self, ontology, question, receiver_id, language="English"):
        message = FipaAclMessage(
            performative="query-ref",
            sender = AgentIdentifier(name=self.agent_id),
            receiver = Receiver([AgentIdentifier(name=receiver_id)]),
            content = question,
            language = language,
            ontology = ontology,
        )
        self._send_msg(q_name="q-knw",key="FIPA-ACL",msg=message)
        
    def get_kb_question(self):
        message = self._receive_msg("q-knw")
        return message.to_dict()

    def send_request(self, ontology, request, receiver_id, language="English"):
        message = FipaAclMessage(
            performative="request",
            sender = AgentIdentifier(name=self.agent_id),
            receiver = Receiver([AgentIdentifier(name=receiver_id)]),
            content = request,
            language = language,
            ontology = ontology,
        )
        self._send_msg(q_name="q-req",key="FIPA-ACL",msg=message)

    def get_request(self):
        message = self._receive_msg("q-req")
        return message.to_dict()