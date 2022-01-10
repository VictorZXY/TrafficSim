from typing import List
import numpy as np
import matplotlib.pyplot as plt

from simulator.car import Car
from simulator.junction import Junction
from simulator.road import Road
from simulator.network import Network
from simulator.schedule import PeriodicSchedule


class Simulator:
    def __init__(self, network: Network = None, cars: List[Car] = None, sim_len=100):
        self.network = network
        self.cars = cars
        self.sim_len = sim_len
        self.clock = 0

    def initialize_from_text(self, filepath):
        network = Network()
        with open(filepath, 'r') as f:
            # Google Hash Code input file contains bonus points for each car
            # that reaches its destination before duration ends. In our
            # simulator, this bonus is neglected.

            # Initialize network
            network.junctions = []
            network.roads = []
            road_name_idx_dict = {}

            duration, junction_num, road_num, car_num, _ = \
                tuple(map(int, f.readline().strip().split()))

            for i in range(junction_num):
                network.junctions.append(Junction(name=f'junction_{i}'))

            for i in range(road_num):
                line = f.readline().strip().split()
                origin_junction_idx = int(line[0])
                exit_junction_idx = int(line[1])
                road_name = line[2]
                road_length = int(line[3])

                origin_junction = network.junctions[origin_junction_idx]
                exit_junction = network.junctions[exit_junction_idx]
                road = Road(name=road_name, length=road_length,
                            origin=origin_junction, exit=exit_junction)
                assert road_name not in road_name_idx_dict
                road_name_idx_dict[road_name] = i
                network.roads.append(road)
                origin_junction.out_rds.append(road)
                exit_junction.in_rds.append(road)

            # Initialize cars
            cars = []
            for i in range(car_num):
                line = f.readline().strip().split()
                assert len(line) == int(line[0]) + 1

                route = []
                for road_name in line[1:]:
                    road_idx = road_name_idx_dict[road_name]
                    road = network.roads[road_idx]
                    route.append(road)

                car = Car(name=f'car_{i}', route=route)
                cars.append(car)

                # Each car starts at the end of the first street (i.e. it waits
                # for the green light to move to the next street)
                car.dist = route[0].length
                route[0].enqueue(car)

            # Pass network and cars to simulator instance
            self.network = network
            self.cars = cars

    def initialize_random_ring(self, junction_num, car_num):
        self.network = Network.generate_ring_network(junction_num=junction_num)
        self.cars = [Car(i).gen_route(self.network) for i in range(car_num)]

    def tick(self):
        for junction in self.network.junctions:
            junction.tick(self.clock)
        for car in self.cars:
            car.tick()
        self.clock += 1

    def simulate(self, schedule_map):
        for junction in self.network.junctions:
            # red_duration = red_duration_map[junction]
            # green_duration = self.cycle_len - red_duration
            junction.schedule = schedule_map[junction]
        for self.clock in range(self.sim_len):
            self.tick()
        return self.get_reward()

    def simulate_uniform(self, red_len, green_len):
        schedule_map = {}
        for junction in self.network.junctions:
            schedule_map[junction] = PeriodicSchedule(junction, [red_len, green_len])
        self.simulate(schedule_map)
        return self.get_reward()

    def get_reward(self):
        return sum([car.reward for car in self.cars])

    def reset(self):
        for car in self.cars:
            car.reset()
        for road in self.network.roads:
            road.reset()
        self.clock = 0


if __name__ == "__main__":
    simulator = Simulator()
    simulator.initialize_random_ring(junction_num=3, car_num=100)

    x = range(11)
    y = range(11)
    z = range(11)
    X, Y, Z = np.meshgrid(x, y, z)
    XYZ = np.array([X.flatten(), Y.flatten(), Z.flatten()]).T
    junctions = simulator.network.junctions

    reward = []
    for xyz in XYZ:
        simulator.reset()
        red_duration_map = {junctions[i]: xyz[i] for i in range(3)}
        simulator.simulate(red_duration_map)
        reward.append(simulator.get_reward())

    ax = plt.axes(projection='3d')
    max_reward = max(reward)
    print(max_reward)
    print(XYZ[reward.index(max_reward)])
    # reward = np.array(reward)/max_reward
    print(reward)
    ax.scatter(X, Y, Z, c=reward, cmap='YlOrRd', alpha=1)
    plt.show()
