# Author: Max Greenwald, Pulkit Jain
# 11/29/2018
#
# Module to communicate with the server

# package imports
import asyncio
import threading

from ..game import state
from .renderer import Renderer
from .socket import Socket

class Client(object):
    """Client defines how each client can interact with the server

    It is defined by the following attributes:
    - renderer: the Renderer that the client will use to display the game
                this also contains the track itself
    - id: the ID it has on the track in the server
    - websocket: the connection to the server
    """
    def __init__(self):
        self.renderer  = Renderer(state.Track())
        self.id        = None
        self.websocket = None

    def join_game(self, host, port):
        self.websocket = 0

def _run_socket(receive_message, outgoing_message, host, port):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    socket = asyncio.get_event_loop().run_until_complete(Socket.connect(host, port))
    asyncio.get_event_loop().run_until_complete(socket.run(receive_message, outgoing_message))

def run_socket(receive_message, outgoing_message, host='localhost', port=8765):
    socket = threading.Thread(target=_run_socket, args=[receive_message, outgoing_message, host, port])
    socket.start()
    return socket
