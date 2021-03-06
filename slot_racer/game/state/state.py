# Author: Max Greenwald, Nathan Allen, Pulkit Jain
# 11/12/2018
#
# Module to define the game's state


# package imports
from .extra import FallData, Event
from ..physics import physics
import copy


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
    - accelerate(gametime): Changes the Car to reflect acceleration
    - stop_accelerating(gametime): Changes the Car to reflect stoppage of
          acceleration
    - fall(speed, distance, gametime): Sets the fallen attribute in the case of
          a fall
    - get_posn(): Returns the x, y coordinates for the distance of the car
    - append_events(events, gametime): Update events from the server
    - get_past_car(gametime): Useful in allowing us to create the lag we
          wanted to simulate in order to allow for updates to not fall prey to
          the actual lag that might exist in network
    - update(gametime): Runs updates on the car periodically, allowing it to
          behave as intended (falling, moving forward etc)
    """

    # global representations independent of each car
    ACCELERATE        = "accelerate"
    STOP_ACCELERATING = "stop_accelerating"

    def __init__(self, idx, model=None):
        self.id              = idx
        self.speed           = 0
        self.distance        = 0
        self.is_accelerating = False
        self.prev_events     = []
        self.fallen          = None
        self.model           = model

    def accelerate(self, gametime):
        self.is_accelerating = True
        self.prev_events.append(Event(self.ACCELERATE, gametime, self.speed,
                                      self.distance))
        print(f'Accelerate: {self.prev_events[-1]}')
        return self.prev_events[-1]

    def stop_accelerating(self, gametime):
        self.is_accelerating = False
        self.prev_events.append(Event(self.STOP_ACCELERATING, gametime,
                                      self.speed, self.distance))
        print(f'Stop Accelerating: {self.prev_events[-1]}')
        return self.prev_events[-1]

    def fall(self, speed, distance, gametime):
        self.is_accelerating = False
        self.fallen = FallData(speed, distance, gametime)
        self.prev_events.append(Event('explode', gametime, 0, self.distance))
        return self.prev_events[-1]

    def get_posn(self):
        return physics.calculate_posn(self)

    def append_events(self, events, gametime):
        self.prev_events.extend(events)
        self.update(gametime)

    # Key function in enforcing explosions;
    # NOTE: never forget to call this before explosion
    def get_past_car(self, gametime):
        # Find first event before the given gametime
        last_event = None
        for event in reversed(self.prev_events):
            if event.timestamp < gametime:
                last_event = event
                break

        # Store a copy of your past to restore ourselves back to
        prev_self = copy.deepcopy(self)
        prev_self.fallen = None

        # Set the car's to where it was at that event
        if last_event:
            prev_self.speed = last_event.speed
            prev_self.distance = last_event.distance
            if last_event.event_type == self.ACCELERATE:
                prev_self.is_accelerating = True
            elif last_event.event_type == 'explode' and gametime - \
                    last_event.timestamp < 1.0:
                prev_self.is_accelerating = False
                print("explode", last_event)
                prev_self.fall(last_event.speed, last_event.distance,
                               last_event.timestamp)
            else:
                prev_self.is_accelerating = False
        prev_self.update(gametime)
        return prev_self

    # Key function for motion/falling off track
    # NOTE: always call this to update the car in regular circumstances
    def update(self, gametime):
        """Gets the new speed and distance of the car.
        - If it has fallen off the track,
            we reset the speed to 0 and leave the distance unchanged. This
            allows us to restart the car from where it fell off on the track.
        - Otherwise we update our car with the new speed and distance
        """
        if physics.falling(self):
            self.speed = 0
            self.fall(self.speed, self.distance, gametime)
        elif self.fallen:
            if gametime > self.fallen.explosion_end:
                self.fallen = None
        else:
            timestep = gametime
            if len(self.prev_events) > 0:
                last_event = self.prev_events[-1]
                self.speed = last_event.speed
                self.distance = last_event.distance
                timestep = gametime - last_event.timestamp
                if last_event.event_type == self.ACCELERATE:
                    self.is_accelerating = True
                else:
                    self.is_accelerating = False
            speed, distance = physics.car_timestep(self, timestep)
            self.speed = speed
            self.distance = distance


class Track(object):
    """A Track is what we will race our Cars on
    An important invariant in our definition is that the id of each car will be
    its index in our participants list
    It is defined by the following attributes:
    - participants: List of Cars participating in the race
          NOTE: As this scales, we might consider migrating this to a dictionary
                to allow for faster lookups and removals
    - lap_distance: The length of a lap. Used to measure the performance of
          different participants
    - model: An image representing the Track. In the future, this could become
          a resizable track using the renderer module
    - track_0_points: Generates the different track points for the 0th car on
          the track
    - track_1_points: Generates the different track points for the 1st car on
          the track

    And by the following behaviours:
    - add_participant(Car): Adds participants to the track and returns its
          index in our participants list
    - remove_participant(idx): Removes participants from the track
    - get_car_by_id(idx): Returns the car corresponding to the entered id
    - check_winner(): Returns the winner if there is one otherwise returns None
    - update_all(gametime): Run an update on every car. This is to be called at
          each timestep
    - generate_track_points(car_id): Returns the points for the track in the
          actual game visual (to be used by Renderer)
    """

    # global representations independent of each track
    DEF_LAP = 10
    DEF_TS  = 0.015

    def __init__(self, num_participants=0, model=None, lap_distance=DEF_LAP):
        self.participants = [Car(i) for i in range(num_participants)]
        self.lap_distance = lap_distance
        self.model        = model
        self.track_0_points = Track.generate_track_points(0)
        self.track_1_points = Track.generate_track_points(1)

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

    def check_winner(self):
        winner = None
        for car in self.participants:
            if car.distance > self.DEF_LAP - 1:
                if winner is None:
                    winner = car
                elif car.distance > winner.distance:
                    winner = car
        return winner

    def update_all(self, gametime):
        if self.participants:
            for car in self.participants:
                car.update(gametime)
        else:
            raise Exception("There are no cars on the track!")

    @staticmethod
    def generate_track_points(car_id):
        dummy = Car(car_id)
        points = []
        for _ in range(600):
            points.append(physics.calculate_posn(dummy))
            dummy.distance += (1 / 600)
        return points
