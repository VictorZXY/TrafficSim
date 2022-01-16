import copy
import random
import re
from typing import List

import networkx as nx
import numpy as np
from matplotlib import pyplot as plt

from simulation.junction import Junction
from simulation.road import Road


class Network:
    """
    Class of a road network, represented as a graph with junctions being its
    vertices and roads being its edges

    Attributes
    ----------
    junctions: junctions in the network
    roads: roads in the network
    """

    def __init__(self, junctions: List[Junction] = None, roads: List[Road] = None):
        self.junctions = junctions or []
        self.roads = roads or []

    @staticmethod
    def generate_network(junction_num, max_road_length=5, allow_cyclic=True):
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
    def generate_random_network(junction_num, max_road_length=5,
                                allow_cyclic=True):
        network = Network()
        network.junctions = []
        network.roads = []

        for i in range(junction_num):
            network.junctions.append(Junction(name=f'junction_{i}'))

        isolated_junctions = set(network.junctions)
        connected_junctions = set()
        for i, exit_junction in enumerate(network.junctions):
            if allow_cyclic:
                isolated_choices = set(list(isolated_junctions))
                connected_choices = set(list(connected_junctions))
            else:
                isolated_choices = isolated_junctions - {exit_junction}
                connected_choices = connected_junctions - {exit_junction}

            if not connected_choices:
                for _ in range(2):
                    origin_junction = random.choice(list(isolated_choices))
                    length = random.randint(1, max_road_length)
                    road = Road.connect(origin_junction, exit_junction, length)
                    network.roads.append(road)
                    isolated_choices.remove(origin_junction)

                    isolated_junctions.remove(origin_junction)
                    connected_junctions.add(origin_junction)
            elif not isolated_choices:
                for _ in range(2):
                    origin_junction = random.choice(list(connected_choices))
                    length = random.randint(1, max_road_length)
                    road = Road.connect(origin_junction, exit_junction, length)
                    network.roads.append(road)
                    connected_choices.remove(origin_junction)
            else:
                origin_junction_1 = random.choice(list(isolated_choices))
                length = random.randint(1, max_road_length)
                road = Road.connect(origin_junction_1, exit_junction, length)
                network.roads.append(road)
                isolated_choices.remove(origin_junction_1)

                origin_junction_2 = random.choice(list(connected_choices))
                length = random.randint(1, max_road_length)
                road = Road.connect(origin_junction_2, exit_junction, length)
                network.roads.append(road)
                connected_choices.remove(origin_junction_2)

                isolated_junctions.remove(origin_junction_1)
                connected_junctions.add(origin_junction_1)

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
            prev = network.junctions[(i - 1) % junction_num]
            next = network.junctions[(i + 1) % junction_num]
            for origin in [prev, next]:
                length = random.randint(1, max_road_length)
                road = Road.connect(origin, junction, length)
                network.roads.append(road)

        return network

    def to_networkx_graph(self):
        G = nx.MultiDiGraph()

        for junction in self.junctions:
            pattern = re.compile('junction_([0-9])+')
            if pattern.match(junction.name.lower()):
                G.add_node(int(junction.name.lower().replace('junction_', '')))
            else:
                assert False

        for road in self.roads:
            origin_junction = road.origin
            exit_junction = road.exit

            pattern = re.compile('junction_([0-9])+')
            if pattern.match(origin_junction.name.lower()) \
                    and pattern.match(exit_junction.name.lower()):
                G.add_edge(
                    int(origin_junction.name.lower().replace('junction_', '')),
                    int(exit_junction.name.lower().replace('junction_', '')),
                    key=road.name,
                    weight=road.length,
                    weight_inv=1 / road.length,
                )
            else:
                assert False

        return G

    def draw(self, node_color='#ffcccc', save_to_filepath=None):
        G = self.to_networkx_graph()
        pos = nx.spring_layout(G, weight='weight_inv')
        edge_labels = {(u, v): data['weight'] for u, v, data in G.edges.data()}
        nx.draw_networkx(G, pos=pos, node_color=node_color)
        nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels)
        plt.axis('off')
        if save_to_filepath:
            plt.savefig(save_to_filepath, bbox_inches='tight')
        plt.show()
