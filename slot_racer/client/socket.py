# Author: Max Greenwald, Pulkit Jain
# 11/30/2018
#
# Module to create a simple interface for persistent socket connections

# package imports
import asyncio
import websockets
import threading

class Queue(object):
    """Implementation of a threadsafe asyncio.Queue()

    It is defined by the following attributes:
    - queue: The asyncio.Queue()
    - mutex: A lock to protect the queue
    """
    def __init__(self):
        self.count = threading.Semaphore(0)
        self.queue = []
        self.mutex = threading.Lock()

    def put(self, item):
        """Since the queue is not capped at a size limit, it is always going
        to complete immediately. This is the reason we make it non-async.
        """
        with self.mutex:
            self.queue.append(item)
            self.count.release()

    def get(self):
        """The queue can be empty at various points in execution. At such a
        situation, we don't want to block the code. We simply want to only
        try to access the queue when we know we can get a proper result.
        """
        self.count.acquire()
        with self.mutex:
            return self.queue.pop(0)


async def start(skt):
    """Creates a socket and initiates and runs it
    :param: client: the client that will be using this socket
    :param: host: host of server
    :param: port: port of server
    :param: receive_message: a function to handle messages received
    :param: outgoing_message: a function to handle messages sent
    """
    await skt.run()
    # TODO: close the socket/deinit the socket??


class Socket(object):
    """Our interface to manage a persistent socket connection

        It is defined by the following attributes:
        - host: string representing the host
        - port: integer representing what port number to connect to
        - connection: the actual websocket
        - swap_time: time to swap execution between receiver and sender

        It is defined by the following behaviors:
        - run(receive_message, outgoing_message): handles the message
              consumption and production
        - _receive_handler(receive_message): handles message consumption
        - _outgoing_message(outgoing_message): handle message production
    """
    def __init__(self, host='localhost', port=8765):
        self.host       = host
        self.port       = port
        self.connection = None
        self.swap_time  = 0.01
        self.inbox      = Queue()
        self.outbox     = Queue()

    def raise_error_uninit(self):
        if not self.connection:
            raise Exception("Socket not started. \n"
                            "USAGE: asyncio.run(socket.start(...) to use this.")

    async def run(self, ):
        self.connection = await websockets.connect(f'ws://{self.host}:{self.port}')
        outbox_thread = threading.Thread(target=self._send_handler)
        outbox_thread.start()
        consumer_task = asyncio.ensure_future(self._receive_handler())
        done, pending = await asyncio.wait(
            [consumer_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()

        # TODO: kill the outbox thread

    async def _receive_handler(self):
        self.raise_error_uninit()
        async for message in self.connection:
            self.inbox.put(message)
            await asyncio.sleep(self.swap_time)

    def _send_handler(self):
        self.raise_error_uninit()
        while True:
            message = self.outbox.get()
            asyncio.run(self.connection.send(message))


