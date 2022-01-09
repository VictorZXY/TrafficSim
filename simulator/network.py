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

    def construct_from_txt_input(self, filepath):
        with open(filepath, 'r') as f:
            # Google Hash Code input file contains bonus points for each car
            # that reaches its destination before duration ends. In our
            # simulator, this bonus is neglected.
            self.junctions = []
            self.roads = []
            road_name_idx_dict = {}

            duration, junction_num, road_num, car_num, _ = \
                tuple(map(int, f.readline().strip().split()))

            for i in range(junction_num):
                self.junctions.append(Junction(name=f'junction_{i}'))

            for i in range(road_num):
                line = f.readline().strip().split()
                origin_junction_idx = int(line[0])
                exit_junction_idx = int(line[1])
                road_name = line[2]
                road_length = int(line[3])

                origin_junction = self.junctions[origin_junction_idx]
                exit_junction = self.junctions[exit_junction_idx]
                road = Road(name=road_name, length=road_length,
                            origin=origin_junction, exit=exit_junction)
                assert road_name not in road_name_idx_dict
                road_name_idx_dict[road_name] = i
                self.roads.append(road)
                origin_junction.out_rds.append(road)
                exit_junction.in_rds.append(road)

            for i in range(car_num):
                line = f.readline().strip().split()
                assert len(line) == int(line[0]) + 1

                route = []
                for road_name in line[1:]:
                    road_idx = road_name_idx_dict[road_name]
                    road = self.roads[road_idx]
                    route.append(road)

                car = Car(name=f'car_{i}', route=route)

                # Each car starts at the end of the first street (i.e. it waits
                # for the green light to move to the next street)
                car.dist = route[0].length
                route[0].enqueue(car)

    def generate_network(self, junction_num, max_road_length=5,
                         circulation=1):
        self.junctions = []
        self.roads = []

        for i in range(junction_num):
            self.junctions.append(Junction(name=f'junction_{i}'))

        road_num = junction_num * 2
        jun_without_in = list(np.random.permutation(junction_num))

        for i in range(road_num):
            length = random.randint(1, max_road_length)
            exit_idx = i // 2
            if len(jun_without_in):
                origin_idx_tmp = jun_without_in.pop()
                if circulation or origin_idx != exit_idx:
                    origin_idx = origin_idx_tmp
                else:
                    origin_idx = jun_without_in.pop()
                    jun_without_in.append(origin_idx_tmp)
            else:
                origin_idx_tmp = random.randint(0, junction_num - 1)
                if circulation or origin_idx != exit_idx:
                    origin_idx = origin_idx_tmp
                else:
                    origin_idx = origin_idx_tmp + 1 if origin_idx_tmp + 1 < junction_num else origin_idx_tmp - 1

            road = Road(name=f'road_{origin_idx}_{exit_idx}', length=length,
                        origin=self.junctions[origin_idx],
                        exit=self.junctions[exit_idx])
            self.junctions[origin_idx].out_rds.append(road)
            self.junctions[exit_idx].in_rds.append(road)
            self.roads.append(road)

        # # simple ring network
        # # flag represents number of times a junction becomes an exit of a road,
        # # which is equivalent to the length of out_rds of the junction
        # flag = [0] * junction_num
        #
        # for i in range(road_num):
        #     length = random.randint(1, max_road_length)
        #     # every junction is exit for two roads
        #     # junction number starts from 0
        #     exit_idx = i // 2
        #     if flag[exit_idx] == 0:
        #         origin_idx = exit_idx + 1 if exit_idx < junction_num - 1 else 0
        #     else:
        #         origin_idx = exit_idx - 1 if exit_idx > 0 else junction_num - 1  # two roads starts from different origins end at exit_idx
        #
        #     flag[exit_idx] += 1
        #
        #     road = Road(name=f'road_{origin_idx}_{exit_idx}', length=length,
        #                 origin=self.junctions[origin_idx],
        #                 exit=self.junctions[exit_idx])
        #     self.junctions[origin_idx].out_rds.append(road)
        #     self.junctions[exit_idx].in_rds.append(road)
        #     self.roads.append(road)
