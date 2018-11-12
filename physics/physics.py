# Nathan Allen
#
# https://www.desmos.com/calculator/fgf5a3kiah
# https://www.desmos.com/calculator/xbqhrdlyea
import math

WIDTH = 4.0
HEIGHT = 2.0
MAX_SPEED = .5
TIME_STEP = 1.0
ACCELLERATION = .1


def falling(r, speed):
    x_comp, y_comp = math.cos(r / WIDTH) * .5, math.cos(r / HEIGHT) * .3
    threshold = math.sqrt(x_comp << 2 + y_comp << 2)
    return speed >= threshold

def colliding(r):
    return False

def calculate_posn(r):
    x = math.sin(r / WIDTH) * HEIGHT
    y = math.sin(r / HEIGHT) * ((WIDTH + HEIGHT) / 10)
    return x, y

def calculate_velocity(r, speed, accellerating):
    if accellerating:
        x = math.cos(r / WIDTH) * .5 * speed
        y = math.cos(r / HEIGHT) * .3 * speed
    else:
        return r
    return min(speed, MAX_SPEED)

def car_timestep(car):
    return car.speed, car.distance
