
WIDTH = 400
HEIGHT = 200


def falling(r, velocity):


def calculate_posn(r):
    x = 600 + math.sin(r / WIDTH) * HEIGHT
    y = HEIGHT + math.sin(r / HEIGHT) * 60
    return x, y
