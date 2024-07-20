import redis
    
class Blackboard:
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = redis.StrictRedis(host=host, port=port, db=db, password="h1qeEKs3TK")

    def write(self, address, data):
        self.client.set(address, data)

    def read(self, address):
        return self.client.get(address)