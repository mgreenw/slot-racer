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
        track.update_all(.015)
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
    track.update_all(.015)
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
    track.update_all(.015)
    for car in track.participants[::2]:
        car.stop_accelerating()
    track.update_all(.015)
    for i in range(1, INIT_LEN - 1):
        prev, car = track.participants[i-1], track.participants[i+1]
        match.append(not car.fallen and car.speed == prev.speed and
            car.distance == prev.distance)

    log(match, test3.__doc__)


def test4():
    """Test 4: Removing car from Track
    """
    track, match = Track(num_participants=INIT_LEN), []
    def_id = 6

    track.remove_participant(def_id)
    for i in track.participants:
        match.append(i.id != def_id)

    try:
        track.remove_participant(def_id)
        match.append(False)
    except:
        match.append(True)

    log(match, test4.__doc__)


def test5():
    """Test 5: Adding car to track by ID
    """
    track, match = Track(num_participants=INIT_LEN), []
    def_id, def_id1 = 16, 2
    matching_ids = [0, 1, 3, 4, 5, 6, 7, 8, 9, 16]

    track.add_participant(Car(def_id-1), def_id)
    track.remove_participant(def_id1)
    for i in range(len(track.participants)):
        match.append(track.participants[i].id == matching_ids[i])

    log(match, test5.__doc__)


def run():
    """Runs all tests"""
    test0()
    test1()
    test2()
    test3()
    test4()
    test5()
