# Author: Pulkit Jain
# 11/12/2018
#
# Module to define extraneous classes, exceptions, and functions the other
# modules need


# package imports
import datetime


class FallData(object):
    """We use this to transfer data required to process the fallout from a car
    falling off

    It is defined by the following attributes:
    - speed: Speed of the car when it fell off
    - distance: R value for the car when it falls off
    """
    def __init__(self, speed, distance):
        self.speed    = speed
        self.distance = distance


class Event(object):
    """An Event is a change in whether we are accelerating or not

    This module is used simply for encapsulating the various details we require
    of each event. These are defined as follows:
    - event_type: A character representing whether we accelerated or stopped
          accelerating
    - timestamp: The time the event happened
    """
    def __init__(self, event_type):
        self.event_type = event_type
        self.timestamp  = datetime.datetime.now()


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
