import unittest
from time import sleep
from agent import Agent  
from utils.kafka import consumer,consume

class TestAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.topic = 'sys-channel'
        cls.consumer = consumer(bootstrap_servers='localhost:9092', group_id="test")

    def test_agent_messages(self):
        agents = [Agent() for _ in range(3)]
        
        sleep(10)

        messages = []

        for i in range(3):
            _, _, message = consume(self.consumer,[self.topic])
            messages.append(message)

        self.assertEqual(len(messages), 3)

        a0 = agents[0]
        a1 = agents[1]

        a0.bus.write('0','data-value')
        data = a1.bus.read('0')
    
        self.assertEqual('data-value', data.decode('ascii'))

        sleep(10)

        messages = []

        for i in range(2):
            _, _, message = consume(self.consumer,[self.topic])
            messages.append(message)

        self.assertEqual(len(messages), 2)

    @classmethod
    def tearDownClass(cls):
        cls.consumer.close()

if __name__ == '__main__':
    unittest.main()
