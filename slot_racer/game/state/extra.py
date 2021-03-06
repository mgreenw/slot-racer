# Author: Nathan Allen, Max Greenwald, Pulkit Jain
# 11/12/2018
#
# Module to define extraneous classes, exceptions, and functions the other
# modules need


class FallData(object):
    """We use this to transfer data required to process the fallout from a car
    falling off

    It is defined by the following attributes:
    - speed: Speed of the car when it fell off
    - distance: R value for the car when it falls off
    - explosion_end: Explosions are supposed to run for 1 unit time, this
          allows us to enforce that
    - sent_to_server: Allows us to represent whether the fall data was
          communicated
    - img_sizes: Enforces how the explosion should grow
    """
    def __init__(self, speed, distance, gametime):
        self.speed    = speed
        self.distance = distance
        self.explosion_end = gametime + 1.0
        self.sent_to_server = False
        self.img_sizes = [
            (3, 3), (9, 8), (11, 14), (14, 24), (15, 19), (14, 19),
            (16, 21), (16, 22), (16, 22), (18, 25), (15, 21), (13, 20),
            (12, 21), (11, 23), (14, 23), (12, 4), (12, 3)
        ]


class Event(object):
    """An Event is a change in whether we are accelerating or not

    This module is used simply for encapsulating the various details we require
    of each event. These are defined as follows:
    - event_type: A character representing whether we accelerated or stopped
          accelerating
    - timestamp: The time the event happened
    - speed: The speed of the car when this event occurred
    - distance: The distance the car had already travelled when this event
          occurred
    """
    def __init__(self, event_type, timestamp, speed=0.0, distance=0.0):
        self.event_type = event_type
        self.timestamp  = timestamp
        self.speed      = speed
        self.distance   = distance

    def __repr__(self):
        return f'<Event type={self.event_type}, timestamp={self.timestamp}, ' \
               f'speed={self.speed}, distance={self.distance}>'


def log(test, msg):
    """Checks if test passed or failed, and reports it
    :param: test: list of booleans representing if all features passed
    :param: msg:  string representing what the test tested
    :return: None
    Eg. test = [True, True, True], msg = "Test1: All cars exist",
            Results in PASSED: {msg}.
        test = [True, False, True], msg = "Test1: All cars exist",
            Results in FAILED: {msg}.
    """
    report = "\033[1m"
    report += "\033[92mPASSED" if all(test) else "\033[91mFAILED"
    report += "\033[0m"
    print("{}\n{}".format(report, msg))
