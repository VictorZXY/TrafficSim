from __future__ import annotations

import random
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from simulator.network import Network
    from simulator.road import Road


class Car:
    """
    Class representing individual cars

    Attributes
    ----------
    name: name of the car
    idx: index of the car's current road on the route
    dist: how far on the road the car has travelled
    route: the route taken by the car
    """

    def __init__(self, name, route: List[Road] = None):
        self.name = name
        self.idx = 0
        self.dist = 0
        self.route = route or []
        self.reward = 0

    def get_road(self):
        return self.route[self.idx]

    def tick(self):
        """ Advance on a road """
        if self.idx < len(self.route):
            if self.dist < self.get_road().length:
                self.dist += 1
                if self.dist == self.get_road().length:
                    self.get_road().enqueue(self)
                self.reward += 1

    def advance(self):
        """ Advance past a junction """
        self.idx += 1
        if self.idx < len(self.route):
            self.dist = 0

    def reset(self):
        self.idx = 0
        self.dist = 0
        self.reward = 0

    def gen_route(self, network: Network, road_num=10):
        if not self.route:
            road = random.choice(network.roads)
            self.dist = road.length
            self.route.append(road)
            road_num -= 1

        road = self.get_road()

        for i in range(road_num):
            road = random.choice(road.exit.out_rds)
            self.route.append(road)

        return self

    def __str__(self):
        return f'Car<{self.name}>'
