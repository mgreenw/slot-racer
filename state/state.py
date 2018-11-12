# Author: Pulkit Jain
# 11/12/2018


# package imports
import math

# local imports
from extra import FallData, Event


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

    def __init__(self, idx, model):
        self.id              = idx
        self.speed           = 0
        self.distance        = 0
        self.is_accelerating = False
        self.prev_events     = [Event(START)]
        self.fallen          = None
        self.model           = model

    def accelerate(self):
        self.is_accelerating = True
        self.prev_events.append(Event(ACCELERATE))

    def stop_accelerating(self):
        self.is_accelerating = False
        self.prev_events.append(Event(STOP_ACCELERATING))

    def fall(self, speed, distance):
        self.fallen = FallData(speed, distance)

    def update(self):
        """
        Gets the new speed and distance of the car.
        - If it has fallen off the track, 
            we reset the speed to 0 and leave the distance unchanged. This
            allows us to restart the car from where it fell off on the track.
        - Otherwise we update our car with the new speed and distance
        """
        speed, distance = physics.car_timestep(self)
        if physics.falling(distance, speed):
            self.speed     = 0
            self.fall(speed, distance)
        else:
            self.speed, self.distance = speed, distance
            self.fallen               = None


class Track(object):
    """A Track is what we will race our Cars on

    It is defined by the following attributes:
    - participants: List of Cars participating in the race
    - lap_distance: The length of a lap. Used to measure the performance of
          different participants
    - model: An image representing the Track. In the future, this could become
          a resizable track using the renderer module

    And by the following behaviours:
    - update_all(): Run an update on every car. This is to be called at each
          timestep
    - resync(participants): Updates our list of participants with the more
          authoritative representation of the server
    """

    # global representations independent of each track
    DEFAULT_LAP = 8 * math.pi

    def __init__(self, model, num_participants, lap_distance=DEFAULT_LAP):
        self.participants = [Car(i, i) for i in range(num_participants)]
        self.lap_distance = lap_distance
        self.model        = model

    def update_all(self):
        for car in participants:
            car.update()
        # CHECK FOR WINNERS
        # Maybe store a cap on the laps we need to compete

    def resync(self, participants):
        """
        This is subject to more change once we have our basic version of the
        game running
        """
        self.participants = participants


