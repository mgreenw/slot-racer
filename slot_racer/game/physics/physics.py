# Nathan Allen
# 27 November 2018

import math


SOCKET_WIDTH = 3
TRACK_WIDTH = 200.0
MAX_SPEED = 0.75
BIG_WIDTH = TRACK_WIDTH / 2.0 + 2.0 * math.sqrt(2) * SOCKET_WIDTH
SMALL_WIDTH = BIG_WIDTH - 4.0 * SOCKET_WIDTH - 4.0 * math.sqrt(2) * SOCKET_WIDTH
RATIO = SMALL_WIDTH / (SMALL_WIDTH + BIG_WIDTH)
ACCELLERATION = 0.2


def falling(car):
    d = car.distance
    if d < RATIO:
        c = 1 - RATIO
        threshold = 1 - (c * math.cos(scale_first_loop(d, c)))
    else:
        c = RATIO
        threshold = 1 + (c * math.cos(scale_second_loop(d, c)))
    return car.speed > threshold

def calculate_posn(car):
    c = RATIO if car.id == 0 else 1 - RATIO
    d = car.distance % 1
    scale_fn = scale_second_loop if (d >= c) else scale_first_loop
    curr_width = BIG_WIDTH if (d >= c) ^ (car.id == 1) else SMALL_WIDTH
    added_multiple = 1.0 if car.id == 0 else -1.0
    x = (((curr_width * math.cos(scale_fn(d, c)))
        / (1 + math.pow(math.sin(scale_fn(d, c)), 2))
        + added_multiple * 2.0 * math.sqrt(2) * SOCKET_WIDTH))
    y = ((curr_width * math.sin(scale_fn(d, c)) * math.cos(scale_fn(d, c)))
        / (1 + math.pow(math.sin(scale_fn(d, c)), 2)))
    return x, y

def scale_first_loop(d, c):
    return (-math.pi) / 2.0 + (d * math.pi) / c

def scale_second_loop(d, c):
    return math.pi / 2.0 + ((d - c) * math.pi) / (1 - c)

def calculate_speed(speed, accellerating, timestep):
    acceleration = ACCELLERATION * timestep
    if accellerating:
        return min(speed + acceleration, MAX_SPEED)
    else:
        return max(speed - acceleration, 0)

def calculate_distance(distance, speed, timestep):
    return distance + (speed * timestep) #TODO: temporary, might want to use method similar to in `falling`

def car_timestep(car, timestep):
    speed = calculate_speed(car.speed, car.is_accelerating, timestep)
    distance = calculate_distance(car.distance % 1.0, car.speed, timestep)
    return speed, distance
