# Author: Pulkit Jain
# 11/12/2018


# package imports
import datetime


class Event(object):
    """An Event is a change in whether we are accelerating or not
    
    This module is used simply for encapsulating the various details we require
    of each event. These are defined as follows:
    - event_type: A character representing whether we accelerated or stopped
          accelerating
    - timestamp: The time the event happened
    """
    def __init__(self, event_type):
        self.event_type = event_type
        self.timestamp  = datetime.datetime.now()


class Car(object):
    """A Car is what will be used to race others on our Track

    It is defined by the following attributes:
    - id: A unique identifier for the car. This is the index of the car in the
          participants attribute of the track
    - speed: The speed of the car at the current time
    - distance: The r distance of the car from the starting point on the track
    - is_accelerating: A boolean representing whether the accelerating event
          is currently happening
    - prev_events: A list of events that have occured prior to the current
          time. This is useful to fix any differences between the server and
          the client. See README for more information
    - last_collision: This is the last time the car ran off the track/had a
          collision. It allows us to reset the car on the track and calculate
          the effects of a collision
    - model: This is an image to represent our car. It defaults to a basic
          image if no choice on this is made by the user

    And the following behaviours:
    - accelerate(): Changes the Car to reflect acceleration
    - stop_accelerating: Changes the Car to reflect stoppage of acceleration
    - collision(): Updates the Car to store the time of collision
    - update(): Uses the physics engine to change the speed and distance of
          the car based on it's current attributes (speed, distance,
          is_accelerating. See physics module for further information)
    """

    # global representations independent of each car
    ACCELERATE        = "A"
    STOP_ACCELERATING = "R"

    def __init__(self, idx, model):
        self.id              = idx
        self.speed           = 0
        self.distance        = 0
        self.is_accelerating = False
        self.prev_events     = []
        self.last_collision  = None
        self.model           = model

    def accelerate(self):
        self.is_accelerating = True
        self.prev_events.append(Event(ACCELERATE))

    def stop_accelerating(self):
        self.is_accelerating = False
        self.prev_events.append(Event(STOP_ACCELERATING))

    def collision(self):
        self.last_collision = datetime.datetime.now()

    def update(self):
        """
        Uses the physics engine to change the speed and distance attributes
        """
        pass


class Track(object):
    """A Track is what we will race our Cars on

    It is defined by the following attributes:
    - participants: List of threads participating in the race. Each thread
          tracks one car
    - lap_distance: The length of a lap. Used to measure the performance of
          different participants
    - model: An image representing the Track. In the future, this could become
          a resizable track using the renderer module

    And by the following behaviours:
    - resync(participants): Updates each car in our list of participants with
          the more authoritative representation of the server
    """

    # global representations independent of each track
    DEFAULT_LAP = 25.1327412  # 8 * pi

    def __init__(self, model, num_participants, lap_distance=DEFAULT_LAP):
        self.participants = [Car(i, i) for i in range(num_participants)]
        self.lap_distance = lap_distance
        self.model        = model

    def resync(self, participants):
        """
        This is subject to more change once we have our basic version of the
        game running
        """
        self.participants = participants


