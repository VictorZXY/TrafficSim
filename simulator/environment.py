from __future__ import annotations

import random
from typing import List

from simulator.network import Network
from simulator.util import get_bin_idx


class Car:
    """
    Class representing individual cars

    Attributes
    ----------
    name: name of the car
    idx: index of the car's current road on the route
    dist: how far down the road the car still needs to travel
    route: the route taken by the car
    """

    def __init__(self, name, route: List[Road] = None):
        self.name = name
        if route is None:
            self.idx = -1
            self.dist = -1
            self.route = []
        else:
            self.idx = 0
            self.dist = route[0].length
            self.route = route

    def get_road(self):
        return self.route[self.idx]

    def advance(self):
        """ Advance on a road """
        if self.dist > 0:
            self.dist -= 1
            if self.dist == 0:
                self.get_road().exit.enqueue(self)

        return self.dist

    def turn(self):
        """ Advance past a junction """
        self.idx += 1
        if self.idx < len(self.route):
            road = self.route[self.idx]
            self.dist = road.length
            return road
        else:
            return None

    def generate_route(self, network: Network, road_num=10):
        if self.idx == -1:
            road = random.choice(network.roads)
            self.idx = 0
            self.dist = road.length
            self.route.append(road)
            road_num -= 1

        road = self.get_road()

        for i in range(road_num):
            road = random.choice(road.exit.out_rds)
            self.route.append(road)


class Road:
    """
    Class representing roads, acting as a queue to record waiting cars

    Attributes
    ----------
    name: name of the road
    length: length of the road
    queue: queue of cars waiting at the road
    origin: starting junction of the road
    exit: ending junction of the road
    """

    def __init__(self, name, length, origin, exit):
        self.name = name
        self.length = length
        self.queue = []
        self.origin = origin
        self.exit = exit

    def deque(self) -> Car:
        return self.queue.pop() if self.queue else None

    def enqueue(self, car: Car):
        self.queue.append(car)

    def __str__(self):
        return f'Road<{self.name}>'


class Junction:
    """
    Analogous to a vertex in the road graph

    Attributes
    ----------
    name: name of the junction
    in_rds: roads into the junction (since this is a directed graph)
    out_rds: roads out of the junction
    schedule: traffic light sequence at this junction
    """

    def __init__(self, name,
                 in_rds: List[Road] = None,
                 out_rds: List[Road] = None,
                 duration: List[int] = None):
        if duration is None:
            duration = []
        if in_rds is None:
            in_rds = []
        if out_rds is None:
            out_rds = []
        self.name = name
        self.out_rds = []
        self.in_rds = []
        assert (len(in_rds) == len(duration))
        self.schedule: Schedule = PeriodicSchedule(self, duration)

    def tick(self, t):
        in_rd = self.schedule.get_incoming_at(t)
        in_rd.deque().turn()

    def __str__(self):
        return f'Junction<{self.name}>'


class Network:
    """
    Class of a road network, represented as a graph with junctions being its
    vertices and roads being its edges

    Attributes
    ----------
    junctions: junctions in the network
    roads: roads in the network
    """

    def __init__(self, junctions: List[Junction] = None,
                 roads: List[Road] = None):
        if junctions is None:
            self.junctions = []
        else:
            self.junctions = junctions

        if roads is None:
            self.roads = []
        else:
            self.roads = roads

    def generate_network(self, junction_num, max_road_length=5):
        self.junctions = []
        for i in range(junction_num):
            self.junctions.append(Junction(name=f'junction_{i}'))

        road_num = junction_num * 2
        # flag represents number of times a junction becomes an exit of a road,
        # which is equivalent to the length of out_rds of the junction
        flag = [0] * junction_num

        for i in range(road_num):
            length = random.randint(1, max_road_length)
            # every junction is exit for two roads
            # junction number starts from 0
            exit_idx = i // 2
            if flag[exit_idx] == 0:
                origin_idx = exit_idx + 1 if exit_idx < junction_num - 1 else 0
            else:
                origin_idx = exit_idx - 1 if exit_idx > 1 else junction_num - 1  # two roads starts from different origins end at exit_idx

            flag[exit_idx] += 1

            road = Road(name=f'road_{origin_idx}_{exit_idx}', length=length,
                        origin=self.junctions[origin_idx],
                        exit=self.junctions[exit_idx])
            self.junctions[origin_idx].out_rds.append(road)
            self.junctions[exit_idx].in_rds.append(road)
            self.roads.append(road)


class Schedule:
    """
    Represent a traffic light schedule at a junction, serves as an interface

    Attributes
    ----------
    junction: each traffic light must be associated with a junction
    schedule: a function that takes in time and output which road the deque should occur
              uses random sampling by default
    """

    def __init__(self, junction: Junction, schedule=None):
        self.junction = junction
        self.schedule = schedule

    def get_incoming_at(self, t):
        if self.schedule:
            return self.schedule(t)
        else:
            return random.choice(self.junction.in_rds)


class PeriodicSchedule(Schedule):
    """
    Represent a traffic light schedule that releases traffic in a round-robin fashion periodically

    Attributes
    ----------
    junction, schedule: same as parent class
    """

    def __init__(self, junction: Junction, duration):
        super().__init__(junction)
        self.schedule = lambda t: self.junction.in_rds[get_bin_idx(duration, t)]
