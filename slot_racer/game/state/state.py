# Author: Pulkit Jain
# 11/12/2018
#
# Module to define the game's state


# package imports
import math

# local imports
from .extra import FallData, Event
from ..physics import physics


class Car(object):
    """A Car is what will be used to race others on our Track

    An important invariant in our definition is that a cars id is also its
    position on the track (innermost track at start has id = 0)

    It is defined by the following attributes:
    - id: This is the index of the car in the participants attribute of the
          track. NOTE invariant defined above
    - speed: The speed of the car at the current time
    - distance: The r distance of the car from the starting point on the track
    - is_accelerating: A boolean representing whether the accelerating event
          is currently happening
    - prev_events: A list of events that have occured prior to the current
          time. This is useful to fix any differences between the server and
          the client. See README for more information
    - fallen: This stores information regarding the last time a car fell off.
          We use this data to process collisions and other effects
    - model: This is an image to represent our car. It defaults to a basic
          image if no choice on this is made by the user

    And the following behaviours:
    - accelerate(): Changes the Car to reflect acceleration
    - stop_accelerating: Changes the Car to reflect stoppage of acceleration
    - fall(): Sets the fallen attribute in the case of a fall
    - update(): Uses the physics engine to change the speed and distance of
          the car based on it's current attributes (speed, distance,
          is_accelerating. See physics module for further information)
    """

    # global representations independent of each car
    START             = "S"
    ACCELERATE        = "A"
    STOP_ACCELERATING = "R"

    def __init__(self, idx, model=None):
        self.id              = idx
        self.speed           = 0
        self.distance        = 0
        self.is_accelerating = False
        self.prev_events     = [Event(self.START)]
        self.fallen          = None
        self.model           = model

    def accelerate(self):
        self.is_accelerating = True
        self.prev_events.append(Event(self.ACCELERATE))

    def stop_accelerating(self):
        self.is_accelerating = False
        self.prev_events.append(Event(self.STOP_ACCELERATING))

    def fall(self, speed, distance):
        self.fallen = FallData(speed, distance)

    def update(self, timestep):
        """Gets the new speed and distance of the car.
        - If it has fallen off the track,
            we reset the speed to 0 and leave the distance unchanged. This
            allows us to restart the car from where it fell off on the track.
        - Otherwise we update our car with the new speed and distance
        """
        speed, distance = physics.car_timestep(self, timestep)
        if physics.falling(self):
            self.speed = 0
            self.fall(speed, distance)
        else:
            self.speed, self.distance = speed, distance
            self.fallen               = None


class Track(object):
    """A Track is what we will race our Cars on

    An important invariant in our definition is that the id of each car will be
    its index in our participants list

    It is defined by the following attributes:
    - participants: List of Cars participating in the race
    - lap_distance: The length of a lap. Used to measure the performance of
          different participants
    - model: An image representing the Track. In the future, this could become
          a resizable track using the renderer module

    And by the following behaviours:
    - add_participant(Car): Adds participants to the track and returns its
          index in our participants list
    - update_all(): Run an update on every car. This is to be called at each
          timestep
    - resync(participants): Updates our list of participants with the more
          authoritative representation of the server
    """

    # global representations independent of each track
    DEF_LAP = 10
    DEF_TS  = 0.015

    def __init__(self, num_participants=0, model=None, lap_distance=DEF_LAP):
        self.participants = [Car(i) for i in range(num_participants)]
        self.lap_distance = lap_distance
        self.model        = model

    def add_participant(self, car, idx=-1):
        if car not in self.participants:
            if 0 <= idx and \
                    not any(map(lambda x: idx == x.id, self.participants)):
                car.id = idx
            else:
                car.id = len(self.participants)
            self.participants.append(car)
        return car.id

    def remove_participant(self, idx):
        car = self.get_car_by_id(idx)
        if car:
            self.participants.remove(car)
        else:
            raise ValueError("Car #{} is not on the Track!".format(idx))

    def get_car_by_id(self, idx):
        for car in self.participants:
            if car.id == idx:
                return car

    def update_all(self, timestep):
        if self.participants:
            cur_ts = 0
            while cur_ts < timestep:
                for car in self.participants:
                    car.update(timestep)
                    if car.distance > self.DEF_LAP:
                        return car.id
                cur_ts += self.DEF_TS
        else:
            raise Exception("There are no cars on the track!")

    def resync(self, participants):
        """This is subject to more change once we have our basic version of the
        game running"""
        self.participants = participants
