import redis

from agentlink.bus.config import BlackboardSettings


class Blackboard:
    def __init__(self, blackboard_config: BlackboardSettings = BlackboardSettings()):
        self.client = redis.StrictRedis(
            host=blackboard_config.dns.host, port=blackboard_config.dns.port, password=blackboard_config.redis_pwd.get_secret_value()
        )

    def write(self, address, data):
        self.client.set(address, data)

    def read(self, address):
        return self.client.get(address)
