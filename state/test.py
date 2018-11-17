# Author: Pulkit Jain
# 11/12/2018
#
# Module to test the game's state


# local imports
from state import Car, Track
from extra import log


def test0():
    """Test0: Car IDs reflect their indices in participants list
       - Initializes correctly
       - Adds cars while maintaining invariant
    """
    INIT_LEN, TEST_LEN = 10, 11
    track, match       = Track(num_participants=INIT_LEN), []

    # initializes correctly
    for idx, car in enumerate(track.participants):
        match.append(car.id == idx)

    # adds cars while maintining invariant
    new_car = Car(TEST_LEN)
    track.add_participant(new_car)
    match.append(track.participants[-1].id == INIT_LEN)

    log(match, test0.__doc__)


def test1():
    """Test1: Track updates and detects collisions correctly
       - Updating track without cars should result in error
    """
    track, match = Track(), []

    # updating track without cars
    try:
        track.update_all()
        match.append(False)
    except:
        match.append(True)

    # check if updates on all cars work if all of them accelerate
    for car in track:
        car.accelerate()
    track.update_all()
    for car in track:
        worked = not car.fallen

    # check if updates on all cars works if some update acceleration

    # check if updates on all cars works if car at edge of track (last car
    # in list) updates so that it falls off the track [[ only outermost car
    # should fall off track ]]

    # check if updates on all cars works if innermost car falls off track
    # [[ multiple cars should fall off track if collision ]]

    log(match, test1.__doc__)


def run():
    """Runs all tests"""
    test0()
    test1()


