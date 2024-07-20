import uuid
from bus.core import Bus

class Agent:

    GENERIC_GROUP = 'generic_group'

    def __init__(self, agent_group=GENERIC_GROUP, agent_id=None):
        if not agent_id:
            agent_id = uuid.uuid4().hex[:8]
        self.bus = Bus(bootstrap_servers='localhost:9092', group_id=agent_group, agent_id=agent_id)