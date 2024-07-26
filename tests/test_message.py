import unittest

from agentlink.bus.message import AgentIdentifier, FipaAclMessage, Receiver


class TestFipaAclMessage(unittest.TestCase):

    def test_fipa_acl_messages(self):

        message = FipaAclMessage(
            performative="inform",
            sender=AgentIdentifier(name="agentsender"),
            receiver=Receiver(),
            content=f"The agent agentsender is now available. You can ask about the following topics: A, B, C",
            language="English",
            ontology="agent-availability",
        )

        msg_json = message.to_json()

        new_message = FipaAclMessage.from_json(msg_json)

        self.assertEqual(message.get_receiver(), new_message.get_receiver())
        self.assertDictEqual(message.to_dict(), new_message.to_dict())

    def test_json_message(self):
        jmsg = """{
            "performative": "query-ref",
            "sender": "(agent-identifier :name 'agent0')",
            "receiver": "(set [(agent-identifier :name 'eadd9034-1b60-41e3-b848-1eba174894c6')])",
            "content": "question",
            "language": "English",
            "ontology": "question"
        }"""

        msg = FipaAclMessage.from_json(jmsg)
        rec = msg.get_receiver()
        self.assertEqual(str(rec), "eadd9034-1b60-41e3-b848-1eba174894c6")


if __name__ == "__main__":
    unittest.main()
