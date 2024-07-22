import unittest
from agent import Agent

class TestApplication(unittest.TestCase):

    def test_application(self):

        a0 = Agent(
            agent_id="agent0",
            topics=["general-kb"]
        )

        a1 = Agent(
            agent_id="agent1",
            topics=["specific-kb"]
        )

        sys_info = a0.get_sys_info()
        self.assertEqual('(agent-identifier :name "agent1")',sys_info["sender"])        
        
        a0.ask_kb("question","question","agent1")
        question = a1.get_kb_question()
        self.assertEqual('(agent-identifier :name "agent0")',question["sender"])
        self.assertEqual('question',question["content"])  

        a1.send_request("request","request","agent0")
        request = a0.get_request()
        self.assertEqual('(agent-identifier :name "agent1")',request["sender"])
        self.assertEqual('request',request["content"])  

if __name__ == '__main__':
    unittest.main()
