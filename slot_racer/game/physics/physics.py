# Nathan Allen
# 6 December 2018
#
# Physics library for game state and rendering

import math


SOCKET_WIDTH = 3
TRACK_WIDTH = 200.0
MAX_SPEED = 0.75
BIG_WIDTH = TRACK_WIDTH / 2.0 + 2.0 * math.sqrt(2) * SOCKET_WIDTH
SMALL_WIDTH = BIG_WIDTH - 4.0 * SOCKET_WIDTH - 4.0 * math.sqrt(2) * SOCKET_WIDTH
RATIO = SMALL_WIDTH / (SMALL_WIDTH + BIG_WIDTH)
ACCELERATION = 0.2


def falling(car):
    """Determines whether or not the car is falling.
    """
    return car.speed > threshold(car)

def threshold(car):
    d = car.distance % 1
    switch = RATIO if car.id == 0 else 1 - RATIO
    c, scale_fn = ((switch, scale_second_loop) if d >= switch
        else ((1 - switch), scale_first_loop))
    if (d < switch):
        threshold = 1 - (c * math.cos(scale_fn(d, switch)))
    else:
        threshold = 1 + (c * math.cos(scale_fn(d, switch)))
    return threshold

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

def calculate_speed(speed, accelerating, timestep):
    acceleration = ACCELERATION * timestep
    if accelerating:
        return min(speed + acceleration, MAX_SPEED)
    else:
        return max(speed - acceleration, 0)

def calculate_distance(distance, initial_speed, accelerating, timestep):
    if accelerating:
        return (distance + (initial_speed * timestep) +
            .5 * ACCELERATION * math.pow(timestep, 2))
    else:
        time_until_stop = initial_speed / ACCELERATION
        if time_until_stop > timestep:
            return (distance + (initial_speed * timestep) -
                .5 * ACCELERATION * math.pow(timestep, 2))
        else:
            return (distance + (initial_speed * time_until_stop) -
                .5 * ACCELERATION * math.pow(time_until_stop, 2))

def car_timestep(car, timestep):
    """Gets the new speed and distance of the car after a set amount of time.
    """
    distance = calculate_distance(car.distance, car.speed,
                                  car.is_accelerating, timestep)
    speed = calculate_speed(car.speed, car.is_accelerating, timestep)
    return speed, distance
