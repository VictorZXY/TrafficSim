import random

import numpy as np
import GPy

from GPyOpt.methods import BayesianOptimization

from simulation.simulator import Simulator

random.seed(42)
network_options = ['text', 'random', 'ring']
network_type = 'random'
junction_num = 40
car_num = 100

simulator = Simulator()
if network_type == 'random':
    simulator.initialize_random_network(junction_num=junction_num, car_num=car_num)
elif network_type == 'random_ring':
    simulator.initialize_random_ring(junction_num=junction_num, car_num=car_num)
elif network_type == 'text':
    simulator.initialize_from_text('../data/f.txt')
    junction_num = len(simulator.network.junctions)
else:
    raise NameError('Invalid network option')


def optimize(max_iter=300, mode_num=3):
    def f1(x):
        simulator.reset()
        x = list(map(int, x))
        red_lens = range(1, mode_num + 1)
        green_lens = list(reversed(red_lens))
        simulator.simulate_preset(red_lens, green_lens, x)
        return -simulator.get_reward()

    domain = [{
        'name': f'mode_{i}',
        'type': 'discrete',
        'domain': range(0, mode_num)
    } for i in range(junction_num)]
    opt1 = BayesianOptimization(f=lambda X: np.apply_along_axis(f1, 1, X),
                                domain=domain, model_type='sparseGP', initial_design_numdata=80,
                                acquisition_type='EI')
    opt1.run_optimization(max_iter=max_iter, max_time=300)
    opt1.plot_convergence()
    print(opt1.x_opt)
    print(opt1.fx_opt)

    def f2(x):
        simulator.reset()
        x = list(map(int, x))
        mode = list(map(int, opt1.x_opt))
        red_lens = x[::2]
        green_lens = x[1::2]
        simulator.simulate_preset(red_lens, green_lens, mode)
        return -simulator.get_reward()

    domain = []
    for i in range(mode_num):
        domain.append({
            'name': f'red_{i}',
            'type': 'discrete',
            'domain': range(1, 60)
        })
        domain.append({
            'name': f'green_{i}',
            'type': 'discrete',
            'domain': range(1, 60)
        })
    opt2 = BayesianOptimization(f=lambda X: np.apply_along_axis(f2, 1, X),
                                domain=domain, model_type='GP', initial_design_numdata=80,
                                acquisition_type='EI')
    opt2.run_optimization(max_iter=max_iter, max_time=300)
    opt2.plot_convergence()
    print(opt2.x_opt)
    print(opt2.fx_opt)


optimize()
