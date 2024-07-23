import unittest

from utils.kafka import consume, consumer

from agentlink.agent import Agent


class TestAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.topic = "sys-channel"
        cls.consumer = consumer(bootstrap_servers="localhost:9092", group_id="test")

    def test_agent_messages(self):
        agents = [Agent() for _ in range(3)]

        messages = []

        for i in range(3):
            _, _, message = consume(self.consumer, [self.topic])
            messages.append(message)

        self.assertEqual(len(messages), 3)

        a0 = agents[0]
        a1 = agents[1]

        a0.write("0", "data-value")
        data = a1.read("0")

        self.assertEqual("data-value", data.decode("ascii"))

        messages = []

        for i in range(2):
            _, _, message = consume(self.consumer, [self.topic])
            messages.append(message)

        self.assertEqual(len(messages), 2)

    @classmethod
    def tearDownClass(cls):
        cls.consumer.close()


if __name__ == "__main__":
    unittest.main()
