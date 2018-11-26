# Author: Pulkit Jain
# 11/12/2018
#
# Module to test the game's state


# local imports
from .state import Car, Track
from .extra import log

# global definitions
INIT_LEN = 10


def test0():
    """Test0: Car IDs reflect their indices in participants list
       - Initializes correctly
       - Adds cars while maintaining invariant
    """
    track, match = Track(num_participants=INIT_LEN), []
    test_id      = 111

    # initializes correctly
    for idx, car in enumerate(track.participants):
        match.append(car.id == idx)

    # adds cars while maintining invariant
    new_car = Car(test_id)
    track.add_participant(new_car)
    match.append(track.participants[-1].id == INIT_LEN)

    log(match, test0.__doc__)


def test1():
    """Test1: Updating track without cars should result in error
    """
    track, match = Track(), []

    try:
        track.update_all()
        match.append(False)
    except:
        match.append(True)

    log(match, test1.__doc__)


def test2():
    """Test2: Updating cars works with acceleration
    """
    track, match = Track(num_participants=INIT_LEN), []

    for car in track.participants:
        car.accelerate()
    track.update_all()
    for i in range(1, INIT_LEN):
        prev, car = track.participants[i-1], track.participants[i]
        match.append(not car.fallen and car.speed == prev.speed and 
            car.distance == prev.distance)

    log(match, test2.__doc__)


def test3():
    """Test 3: Updating cars works with deceleration
    """
    track, match = Track(num_participants=INIT_LEN), []

    for car in track.participants:
        car.accelerate()
    track.update_all()
    for car in track.participants[::2]:
        car.stop_accelerating()
    track.update_all()
    for i in range(1, INIT_LEN - 1):
        prev, car = track.participants[i-1], track.participants[i+1]
        match.append(not car.fallen and car.speed == prev.speed and
            car.distance == prev.distance)

    log(match, test3.__doc__)


def test4():
    """Contingent on physics fixing up collisions
    """
    # check if updates on all cars works if car at edge of track (last car
    # in list) updates so that it falls off the track [[ only outermost car
    # should fall off track ]]


def test5():
    """Contingent on physics fixing up collisions
    """
    # check if updates on all cars works if innermost car falls off track
    # [[ multiple cars should fall off track if collision ]]


def run():
    """Runs all tests"""
    test0()
    test1()
    test2()
    test3()


