import random
from typing import List
import numpy as np

from simulator.car import Car
from simulator.junction import Junction
from simulator.road import Road


class Network:
    """
    Class of a road network, represented as a graph with junctions being its
    vertices and roads being its edges

    Attributes
    ----------
    junctions: junctions in the network
    roads: roads in the network
    cars: cars in the network
    """

    def __init__(self, junctions: List[Junction] = None,
                 roads: List[Road] = None, cars: List[Car] = None):
        self.junctions = junctions or []
        self.roads = roads or []

    @staticmethod
    def generate_network(junction_num, max_road_length=5, allow_cyclic=1):
        network = Network()
        network.junctions = []
        network.roads = []
        network.cars = []

        for i in range(junction_num):
            network.junctions.append(Junction(name=f'junction_{i}'))

        road_num = junction_num * 2
        jun_without_in = list(np.random.permutation(junction_num))

        for i in range(road_num):
            length = random.randint(1, max_road_length)
            exit_idx = i // 2
            if len(jun_without_in):
                origin_idx_tmp = jun_without_in.pop()
                if allow_cyclic or origin_idx != exit_idx:
                    origin_idx = origin_idx_tmp
                else:
                    origin_idx = jun_without_in.pop()
                    jun_without_in.append(origin_idx_tmp)
            else:
                origin_idx_tmp = random.randint(0, junction_num - 1)
                if allow_cyclic or origin_idx != exit_idx:
                    origin_idx = origin_idx_tmp
                else:
                    origin_idx = origin_idx_tmp + 1 if origin_idx_tmp + 1 < junction_num else origin_idx_tmp - 1

            road = Road(name=f'road_{origin_idx}_{exit_idx}', length=length,
                        origin=network.junctions[origin_idx],
                        exit=network.junctions[exit_idx])
            network.junctions[origin_idx].out_rds.append(road)
            network.junctions[exit_idx].in_rds.append(road)
            network.roads.append(road)
        return network

    @staticmethod
    def generate_random_network(junction_num, max_road_length=5, allow_cyclic=True):
        network = Network()
        network.junctions = []
        network.roads = []

        for i in range(junction_num):
            network.junctions.append(Junction(name=f'junction_{i}'))

        isolated_junctions = set(network.junctions)
        connected_junctions = set()
        for junction in network.junctions:
            for population in [isolated_junctions, connected_junctions]:
                origin = population.pop()
                connected_junctions.add(origin)
                length = random.randint(1, max_road_length)
                road = Road.connect(origin, junction, length)
                network.roads.append(road)

        return network

    @staticmethod
    def generate_ring_network(junction_num, max_road_length=5):
        network = Network()
        network.junctions = []
        network.roads = []

        for i in range(junction_num):
            network.junctions.append(Junction(name=f'junction_{i}'))

        for i in range(junction_num):
            junction = network.junctions[i]
            prev = network.junctions[(i-1) % junction_num]
            next = network.junctions[(i+1) % junction_num]
            for origin in [prev, next]:
                length = random.randint(1, max_road_length)
                road = Road.connect(origin, junction, length)
                network.roads.append(road)

        return network
