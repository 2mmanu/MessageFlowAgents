import unittest
from time import sleep

from agentlink.agent import Agent


class TestApplication(unittest.TestCase):

    def test_application(self):

        a0 = Agent(agent_id="agent0", topics=["general-kb"])

        a1 = Agent(agent_id="eadd9034-1b60-41e3-b848-1eba174894c6", topics=["specific-kb"])

        sleep(5)

        a0.ask_kb("question", "question", "eadd9034-1b60-41e3-b848-1eba174894c6")
        question = a1.get_kb_question()
        self.assertEqual("(agent-identifier :name agent0)", question["sender"])
        self.assertEqual("question", question["content"])

        a1.send_request("request", "request", "agent0")
        request = a0.get_request()
        self.assertEqual("(agent-identifier :name eadd9034-1b60-41e3-b848-1eba174894c6)", request["sender"])
        self.assertEqual("request", request["content"])


if __name__ == "__main__":
    unittest.main()
