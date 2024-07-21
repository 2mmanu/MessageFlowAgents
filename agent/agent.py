import uuid
import queue
from bus.core import Bus
from bus.queue import QueueManager
from bus.blackboard import Blackboard

class Agent:

    _REQ_CH_TOPIC = "req-channel"
    _KNW_CH_TOPIC = "knw-channel"
    _SYS_CH_TOPIC = "sys-channel"

    def __init__(self, agent_id=None):
        
        if not agent_id:
            agent_id = uuid.uuid4().hex[:8]
        self.agent_id = agent_id
        
        self._blackboard = Blackboard()
        
        self._qm = QueueManager()
        self._qm.create_queues("q-req")
        self._qm.create_queues("q-knw")
        self._qm.create_queues("q-sys")
        
        self._bus_req = Bus(self._qm.get_queues("q-req"),
                            self._REQ_CH_TOPIC,
                            bootstrap_servers='localhost:9092',
                            group_id=f"{self.agent_id}r",
                            )
        self._bus_knw = Bus(self._qm.get_queues("q-knw"),
                            self._KNW_CH_TOPIC,
                            bootstrap_servers='localhost:9092',
                            group_id=f"{self.agent_id}k",
                            )
        self._bus_sys = Bus(self._qm.get_queues("q-sys"),
                            self._SYS_CH_TOPIC,
                            bootstrap_servers='localhost:9092',
                            group_id=f"{self.agent_id}s",
                            )
        self._bus_req.start()
        self._bus_knw.start()
        self._bus_sys.start()
        self._hello_word_message()        

    def _informative_msg(self,content, ontology):
        msg = f"""
        (inform
            :performative "inform"
            :sender (agent-identifier :name {self.agent_id})
            :receiver (set (agent-identifier :name :all))
            :content "{content}"
            :language English
            :ontology {ontology}
        )
        """
        return msg
    
    def _send_msg(self,q_name,key,msg):
        q_out = self._qm.get_queue(name=q_name,direction="out")
        q_out.put((key,msg))
        q_out.join()
    
    def _receive_msg(self,q_name):
        q_in = self._qm.get_queue(name=q_name,direction="in")
        return q_in.get()
    
    def _hello_word_message(self):
        self._send_msg(
            q_name="q-sys",
            key="FIPA-ACL",
            msg=self._informative_msg(f"New agent available: {self.agent_id}","AgentAvailability")
            )
    
    def write(self, address, data):
        self._blackboard.write(address, data)
        self._send_msg(
            q_name="q-sys",
            key="FIPA-ACL",
            msg=self._informative_msg(f"Data written to {address} by {self.agent_id}","Notification")
            )

    def read(self, address):
        data = self._blackboard.read(address)
        self._send_msg(
            q_name="q-sys",
            key="FIPA-ACL",
            msg=self._informative_msg(f"Data accessed at  {address} by {self.agent_id}","Notification")
            )
        return data
    
    def ask_kb(self,question):
        self._send_msg(
            q_name="q-knw",
            key="message",
            msg=question
            )
        # return self._receive_msg(
        #     q_name="q-knw"
        # )
    
    def send_request(self,request):
        self._send_msg(
            q_name="q-req",
            key="request",
            msg=request
            )