
# I want a python module which can 1) construct a message
# and 2) reconstruct a dumped message

import json
from collections import namedtuple

Message = namedtuple('Message', ['subject', 'data'])

class Serializer(object):
    def compose(self, subject, data):
        return json.dumps((subject, data))

    def read(self, message):
        parsed = json.loads(message)
        return Message(subject=parsed[0], data=parsed[1])
        pass
