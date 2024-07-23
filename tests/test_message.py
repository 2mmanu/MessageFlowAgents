import unittest

from agentlink.bus.message import AgentIdentifier, FipaAclMessage, Receiver


class TestFipaAclMessage(unittest.TestCase):

    def test_fipa_acl_messages(self):

        message = FipaAclMessage(
            performative="inform",
            sender=AgentIdentifier(name="agent-sender"),
            receiver=Receiver(),
            content=f"The agent agent-sender is now available. You can ask about the following topics: A, B, C",
            language="English",
            ontology="agent-availability",
        )

        msg_json = message.to_json()

        new_message = FipaAclMessage.from_json(msg_json)

        self.assertEqual(message.get_receiver(), new_message.get_receiver())
        self.assertEqual(message.to_json(), new_message.to_json())


if __name__ == "__main__":
    unittest.main()
