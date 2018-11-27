# Nathan Allen
# 27 November 2018

import math

SOCKET_WIDTH = 1
TRACK_WIDTH = 200.0
MAX_SPEED = .5
BIG_WIDTH = TRACK_WIDTH / 2.0 + 2.0 * math.sqrt(2) * SOCKET_WIDTH
SMALL_WIDTH = BIG_WIDTH - 4.0 * SOCKET_WIDTH - 4.0 * math.sqrt(2) * SOCKET_WIDTH
RATIO = SMALL_WIDTH / (SMALL_WIDTH + BIG_WIDTH)
ACCELLERATION = 1


def falling(car):
    d = car.distance
    if d < RATIO:
        c = 1 - RATIO
        threshold = 1 - (c * math.cos(scale_small_loop(d, c)))
    else:
        c = RATIO
        threshold = 1 + (c * math.cos(scale_big_loop(d, c)))
    return car.speed > threshold

def colliding(d):
    return False

def calculate_posn(car):
    c = RATIO if car.id == 0 else 1 - RATIO
    d = car.distance
    curr_width, scale_fn = ((BIG_WIDTH, scale_big_loop) if d >= c
        else (SMALL_WIDTH, scale_small_loop))
    x = (((curr_width * math.cos(scale_fn(d, c)))
        / (1 + math.pow(math.sin(scale_fn(d, c)), 2))
        + 2.0 * math.sqrt(2) * SOCKET_WIDTH))
    y = ((curr_width * math.sin(scale_fn(d, c)) * math.cos(scale_fn(d, c)))
        / (1 + math.pow(math.sin(scale_fn(d, c)), 2)))
    return x, y

def scale_small_loop(d, c):
    return (-math.pi) / 2.0 + (d * math.pi) / c

def scale_big_loop(d, c):
    return math.pi / 2.0 + ((d - c) * math.pi) / (1 - c)

def calculate_speed(speed, accellerating, timestep):
    acceleration = ACCELLERATION * timestep
    if accellerating:
        return min(speed + acceleration, MAX_SPEED)
    else:
        return max(speed - acceleration, 0)

def calculate_distance(distance, speed, timestep):
    return distance + (speed * timestep) #TODO: temporary, might want to use method similar to in `falling`

<<<<<<< HEAD
def car_timestep(car):
    speed = calculate_velocity(car.speed, car.is_accelerating)
    distance = calculate_distance(car.distance, car.speed)
=======
def car_timestep(car, timestep):
    speed = calculate_speed(car.speed, car.is_accelerating, timestep)
    distance = calculate_distance(car.distance, car.speed, timestep)
>>>>>>> master
    return speed, distance
