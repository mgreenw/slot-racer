# Nathan Allen
#
# https://www.desmos.com/calculator/fgf5a3kiah
# https://www.desmos.com/calculator/xbqhrdlyea
# https://www.desmos.com/calculator/1ohpl1uzqj
import math

WIDTH = 4.0
HEIGHT = 2.0
MAX_SPEED = .5
TIME_STEP = 1.0
ACCELLERATION = .1


SOCKET_WIDTH = .5
TRACK_WIDTH = 20
BIG_WIDTH = TRACK_WIDTH / 2.0 + 2.0 * math.sqrt(2) * TRACK_WIDTH
SMALL_WIDTH = BIG_WIDTH - 4.0 * SOCKET_WIDTH
# c = SMALL_WIDTH / (SMALL_WIDTH + BIG_WIDTH)


def falling(d, speed):
    x_comp, y_comp = math.cos(d / WIDTH) * .5, math.cos(d / HEIGHT) * .3
    threshold = math.sqrt(x_comp << 2 + y_comp << 2)
    return speed >= threshold

def colliding(d):
    return False

def calculate_posn(car):
    c = ((SMALL_WIDTH if car.get_id() == 0 else BIG_WIDTH)
        / (SMALL_WIDTH + BIG_WIDTH))
    d = car.distance
    curr_width, scale_fn = ((BIG_WIDTH, scale_big_loop) if d >= c
        else (SMALL_WIDTH, scale_small_loop))
    x = (((curr_width * math.cos(scale_fn(d, c)))
        / (1 + (math.sin(scale_fn(d, c)) << 2)))
        + 2.0 * math.sqrt() * SOCKET_WIDTH)
    y = ((curr_width * math.sin(scale_fn(d, c)) * math.cos(scale_fn(d, c)))
        / (1 + (math.sin(scale_fn(d, c)) << 2)))
    return x, y

def scale_small_loop(d, c):
    return (-math.pi) / 2.0 + (d * math.pi) / c

def scale_big_loop(d, c):
    return math.pi / 2.0 + ((d - c) * math.pi) / (1 - c)

def calculate_velocity(d, speed, accellerating):
    if accellerating:
        x = math.cos(d / WIDTH) * .5 * speed
        y = math.cos(d / HEIGHT) * .3 * speed
    else:
        return d
    return min(speed, MAX_SPEED)

def car_timestep(car):
    return car.speed, car.distance
