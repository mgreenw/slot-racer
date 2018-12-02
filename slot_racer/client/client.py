# Author: Max Greenwald, Pulkit Jain
# 11/29/2018
#
# Module to communicate with the server

# package imports
import asyncio
import threading
from ..game import state
from .renderer import Renderer
from .socket import start
from .protocol import get_protocol


class Client(object):
    """Client defines how each client can interact with the server

    It is defined by the following attributes:
    - renderer: the Renderer that the client will use to display the game
                this also contains the track itself
    - id: the ID it has on the track in the server
    - websocket: the connection to the server

    A brief guide to our protocol [for more information, go to protocol.py]:
    - ping: returns the latency
    - cars: gets a list of all the car_ids
    - upda: update - basic message passing for debugging purposes

    It is defined by the following behaviours:
    - _run_socket(host, port): Internal function that is spawned on a new thread
          to create a persistent websocket connection to the server
    - receive_message(message): Consumes messages from the server
    - outgoing_message(): Waits for messages to be ready, and sends it asap to
          the server
    - join_game(host, port): Spawns a connection to the server and starts the
          game
    """
    def __init__(self):
        self.id            = None
        self.socket        = None
        self.socket_thread = None
        self.renderer      = Renderer(state.Track())
        self.protected_q   = Queue()
        self.protocol      = get_protocol()

    def _run_socket(self, host, port):
        asyncio.set_event_loop(asyncio.new_event_loop())
        asyncio.get_event_loop().run_until_complete(
            start(self, host, port, self.receive_message, self.outgoing_message))

    def receive_message(self, message):
        print(message)
        self.protected_q.put(message)

    def outgoing_message(self):
        message = self.protected_q.get()
        if message in self.protocol:
            return self.protocol[message](self, message)

    def join_game(self, host='localhost', port=8765):
        self.socket_thread = \
            threading.Thread(target=self._run_socket, args=[host, port])
        self.socket_thread.start()


class Queue(object):
    """Implementation of a threadsafe asyncio.Queue()

    It is defined by the following attributes:
    - queue: The asyncio.Queue()
    - mutex: A lock to protect the queue
    """
    def __init__(self):
        self.queue = asyncio.Queue()
        self.mutex = threading.Lock()

    def put(self, item):
        """Since the queue is not capped at a size limit, it is always going
        to complete immediately. This is the reason we make it non-async.
        """
        self.mutex.acquire()
        self.queue.put_nowait(item)
        self.mutex.release()

    def get(self):
        """The queue can be empty at various points in execution. At such a
        situation, we don't want to block the code. We simply want to only
        try to access the queue when we know we can get a proper result.
        """
        self.mutex.acquire()
        if not self.queue.empty():
            item = self.queue.get_nowait()
        else:
            item = 'EMPTY'
        self.mutex.release()
        return item


