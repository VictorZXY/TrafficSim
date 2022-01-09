from typing import List
import numpy as np
import matplotlib.pyplot as plt

from simulator.car import Car
from simulator.network import Network
from simulator.schedule import PeriodicSchedule


class Simulator:
    def __init__(self, network: Network = None, cars: List[Car] = None, sim_len=100):
        self.network = network
        self.cars = cars
        self.sim_len = sim_len
        self.clock = 0

    def initialize_random_ring(self, junction_num, car_num):
        self.network = Network()
        self.network.generate_ring_network(junction_num=junction_num)
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
