import random
from typing import List

from road import Road


class Car:
    """
    Class representing individual cars

    Attributes
    ----------
    name: name of the car
    road: current road the car is on
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
            road = random.choice(network.junctions)
            self.idx = 0
            self.dist = road.length
            self.route.append(road)
            road_num -= 1

        road = self.get_road()

        for i in range(road_num):
            road = random.choice(road.exit.out_rds)
            self.route.append(road)
