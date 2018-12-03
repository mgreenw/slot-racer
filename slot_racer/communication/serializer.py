# Author: Max Greenwald
# 12/3/2018
#
# Module to serialize our messages to communicate better

# package imports
import json
from collections import namedtuple

# global variables
Message = namedtuple('Message', ['subject', 'data'])


class Serializer(object):
    """Serializer converts messages to required formats [[ incoming vs outgoing ]]

    It is defined by the following behaviours:
    - compose(subject, data): makes a message
    - read(message): parses a message
    """
    def compose(self, subject, data):
        return json.dumps((subject, data))

    def read(self, message):
        parsed = json.loads(message)
        return Message(subject=parsed[0], data=parsed[1])


