# Author: Pulkit Jain
# 12/06/2018
#
# Module to hold all the extra definitions and implementations we use in client


# package imports
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
        to complete immediately. This is the reason we make this non-async.
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


