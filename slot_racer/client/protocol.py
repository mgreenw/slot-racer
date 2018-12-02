# Author: Max Greenwald, Pulkit Jain
# 12/1/2018
#
# Module to define the client protocol

# package imports
import re


def pong(self, msg):
    return 'pong'


def cars_assigned(self, msg):
    print(msg)
    pass


def get_protocol():
    protocol = dict()
    protocol['ping'] = pong
    protocol['cars'] = cars_assigned
    protocol['upda'] = lambda x, y: 'UPDATE'
    return protocol


