import json
import re
from enum import Enum


class Performative(Enum):
    # http://www.fipa.org/specs/fipa00037/SC00037J.html
    """
    Enum representing the performative of a FIPA-ACL message.

    Attributes:
    -----------
    ACCEPT_PROPOSAL : str
        The action of accepting a previously made proposal.
    AGREE : str
        The action of agreeing to a request.
    CANCEL : str
        The action of cancelling a previously proposed action.
    CALL_FOR_PROPOSAL : str
        The action of requesting proposals for a given action.
    CONFIRM : str
        The action of confirming the truth of a proposition.
    DISCONFIRM : str
        The action of disconfirming the truth of a proposition.
    FAILURE : str
        The action of informing that an action has failed.
    INFORM : str
        The action of informing about the truth of a proposition.
    INFORM_IF : str
        The action of informing whether a proposition is true.
    INFORM_REF : str
        The action of informing about the value of a reference.
    NOT_UNDERSTOOD : str
        The action of informing that the message was not understood.
    PROPOSE : str
        The action of proposing a new action.
    QUERY_IF : str
        The action of querying whether a proposition is true.
    QUERY_REF : str
        The action of querying about the value of a reference.
    REFUSE : str
        The action of refusing a request.
    REJECT_PROPOSAL : str
        The action of rejecting a proposal.
    REQUEST : str
        The action of requesting an action to be performed.
    REQUEST_WHEN : str
        The action of requesting an action to be performed when a proposition becomes true.
    REQUEST_WHENEVER : str
        The action of requesting an action to be performed whenever a proposition becomes true.
    SUBSCRIBE : str
        The action of subscribing to be notified of events.
    PROXY : str
        The action of delegating an action to another agent.
    PROPAGATE : str
        The action of propagating a message to other agents.
    """
    ACCEPT_PROPOSAL = "accept-proposal"
    AGREE = "agree"
    CANCEL = "cancel"
    CALL_FOR_PROPOSAL = "call-for-proposal"
    CONFIRM = "confirm"
    DISCONFIRM = "disconfirm"
    FAILURE = "failure"
    INFORM = "inform"
    INFORM_IF = "inform-if"
    INFORM_REF = "inform-ref"
    NOT_UNDERSTOOD = "not-understood"
    PROPAGATE = "propagate"
    PROPOSE = "propose"
    PROXY = "proxy"
    QUERY_IF = "query-if"
    QUERY_REF = "query-ref"
    REFUSE = "refuse"
    REJECT_PROPOSAL = "reject-proposal"
    REQUEST = "request"
    REQUEST_WHEN = "request-when"
    REQUEST_WHENEVER = "request-whenever"
    SUBSCRIBE = "subscribe"


class AgentIdentifier:

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'(agent-identifier :name "{self.name}")'

    @staticmethod
    def get_from_s_expression(expression):
        agent_pattern = re.compile(r'\(agent-identifier\s+:name\s+"([^"]+)"\)')
        agents = [AgentIdentifier(name=name) for name in agent_pattern.findall(expression)]
        return agents[0]


class Receiver:
    def __init__(self, *agents):
        self.agents = agents

    def __repr__(self):
        if not self.agents:
            return "(set (agent-identifier :name :all))"
        return f'(set {" ".join(repr(agent) for agent in self.agents)})'

    @staticmethod
    def get_from_s_expression(expression):
        agent_pattern = re.compile(r'\(agent-identifier\s+:name\s+"([^"]+)"\)')
        agents = [AgentIdentifier(name) for name in agent_pattern.findall(expression)]
        return Receiver(*agents)


class FipaAclMessage:
    """
    A class to represent a FIPA-ACL message.

    Attributes:
    -----------
    performative : Performative
        The performative of the message (e.g., inform, request).
    sender : str
        The sender of the message.
    receiver : str
        The receiver of the message.
    content : str
        The content of the message.
    reply_to : str, optional
        The identifier of the agent to which subsequent messages should be sent.
    language : str, optional
        The language in which the content is expressed.
    encoding : str, optional
        The encoding of the message content.
    ontology : str, optional
        The ontology used to give a meaning to the symbols in the content.
    protocol : str, optional
        The interaction protocol that the sender is employing.
    conversation_id : str, optional
        An identifier for the ongoing sequence of communicative acts.
    reply_with : str, optional
        An identifier that the sender will use to match this message with future responses.
    in_reply_to : str, optional
        An identifier that the sender will use to indicate which message this is a reply to.
    reply_by : str, optional
        A time or deadline by which the sender expects a reply.
    """

    def __init__(
        self,
        performative: Performative,
        sender,
        receiver,
        content,
        reply_to=None,
        language=None,
        encoding=None,
        ontology=None,
        protocol=None,
        conversation_id=None,
        reply_with=None,
        in_reply_to=None,
        reply_by=None,
    ):
        # http://www.fipa.org/specs/fipa00061/SC00061G.html
        self.performative = Performative(performative)
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.reply_to = reply_to
        self.language = language
        self.encoding = encoding
        self.ontology = ontology
        self.protocol = protocol
        self.conversation_id = conversation_id
        self.reply_with = reply_with
        self.in_reply_to = in_reply_to
        self.reply_by = reply_by

    def __repr__(self):
        fields = [
            f':performative "{self.performative.value}"',
            f":sender {repr(self.sender)}",
            f":receiver {repr(self.receiver)}",
            f':content "{self.content}"',
            f":language {self.language}",
            f':ontology "{self.ontology}"',
        ]

        if self.reply_to:
            fields.append(f':reply_to "{self.reply_to}"')
        if self.encoding:
            fields.append(f':encoding "{self.encoding}"')
        if self.protocol:
            fields.append(f':protocol "{self.protocol}"')
        if self.conversation_id:
            fields.append(f':conversation_id "{self.conversation_id}"')
        if self.reply_with:
            fields.append(f':reply_with "{self.reply_with}"')
        if self.in_reply_to:
            fields.append(f':in_reply_to "{self.in_reply_to}"')
        if self.reply_by:
            fields.append(f':reply_by "{self.reply_by}"')

        fields_str = "\n    ".join(fields)
        return f"({self.performative.value}\n    {fields_str}\n)"

    def to_dict(self):
        message_dict = {
            "performative": self.performative.value,
            "sender": repr(self.sender),
            "receiver": repr(self.receiver),
            "content": self.content,
            "reply_to": self.reply_to,
            "language": self.language,
            "encoding": self.encoding,
            "ontology": self.ontology,
            "protocol": self.protocol,
            "conversation_id": self.conversation_id,
            "reply_with": self.reply_with,
            "in_reply_to": self.in_reply_to,
            "reply_by": self.reply_by,
        }
        return {k: v for k, v in message_dict.items() if v is not None}

    def to_json(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def from_dict(message_dict):
        performative = message_dict["performative"]
        sender = AgentIdentifier.get_from_s_expression(message_dict["sender"])
        receiver = Receiver.get_from_s_expression(message_dict.get("receiver"))
        content = message_dict["content"]
        reply_to = message_dict.get("reply_to")
        language = message_dict.get("language")
        encoding = message_dict.get("encoding")
        ontology = message_dict.get("ontology")
        protocol = message_dict.get("protocol")
        conversation_id = message_dict.get("conversation_id")
        reply_with = message_dict.get("reply_with")
        in_reply_to = message_dict.get("in_reply_to")
        reply_by = message_dict.get("reply_by")

        return FipaAclMessage(
            performative=performative,
            sender=sender,
            receiver=receiver,
            content=content,
            reply_to=reply_to,
            language=language,
            encoding=encoding,
            ontology=ontology,
            protocol=protocol,
            conversation_id=conversation_id,
            reply_with=reply_with,
            in_reply_to=in_reply_to,
            reply_by=reply_by,
        )

    @staticmethod
    def from_json(message_json):
        message_dict = json.loads(message_json)
        return FipaAclMessage.from_dict(message_dict)

    def get_receiver(self):
        if not self.receiver or not self.receiver.agents:
            return "all"
        return [agent.name for agent in self.receiver.agents][0]


class FipaAclMessageValidator:
    @staticmethod
    def validate(message):
        required_fields = ["performative", "sender", "receiver", "content"]
        for field in required_fields:
            if not getattr(message, field, None):
                return False, f"Field '{field}' is missing."

        if not isinstance(message.performative, Performative):
            return False, "Invalid performative."

        return True, "Message is valid."
