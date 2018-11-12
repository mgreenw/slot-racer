# Nathan Allen
#
# https://www.desmos.com/calculator/fgf5a3kiah
WIDTH = 4
HEIGHT = 2


def falling(r, velocity):
    x_comp, y_comp = math.cos(r / WIDTH) * 2, math.cos(r / HEIGHT) * .6
    threshold = math.sqrt(x_comp << 2 + y_comp << 2)
    return velocity >= threshold


def calculate_posn(r):
    x = math.sin(r / WIDTH) * HEIGHT
    y = math.sin(r / HEIGHT) * .6
    return x, y
