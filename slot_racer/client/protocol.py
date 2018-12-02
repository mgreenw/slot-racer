# Author: Max Greenwald, Pulkit Jain
# 12/1/2018
#
# Module to define the client protocol


def pong():
    return 'pong'


def get_protocol():
    protocol = dict()
    protocol['ping'] = pong
    protocol['UPDATE'] = lambda: print('UPDATE')
    return protocol


