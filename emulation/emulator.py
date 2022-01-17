import numpy as np
import GPy

from GPyOpt.methods import BayesianOptimization

from simulation.simulator import Simulator

network_options = ['text', 'random', 'ring']
schedule_options = ['uniform', 'distinct', 'preset', 'forced_preset']
network_type = 'random'
junction_num = 40
car_num = 100

simulator = Simulator()
if network_type == 'random':
    simulator.initialize_random_network(junction_num=junction_num, car_num=car_num)
elif network_type == 'random_ring':
    simulator.initialize_random_ring(junction_num=junction_num, car_num=car_num)
elif network_type == 'text':
    simulator.initialize_from_text('../data/a.txt')
    junction_num = len(simulator.network.junctions)
else:
    raise NameError('Invalid network option')


def optimize(schedule_type, max_iter=100, mode_num=3):
    def f(x):
        simulator.reset()
        x = list(map(int, x))
        if network_type == 'text':
            for car in simulator.cars:
                car.dist = car.route[0].length
                car.route[0].enqueue(car)
        if schedule_type == 'uniform':
            simulator.simulate_uniform(x[0], x[1])
        elif schedule_type == 'distinct':
            simulator.simulate_distinct(x[::2], x[1::2])
        elif schedule_type == 'preset':
            simulator.simulate_preset(x[:mode_num], x[mode_num:mode_num * 2], x[mode_num * 2:])
        elif schedule_type == 'forced_preset':
            red_lens = [(int(x[0] * i / (mode_num + 1)) for i in range(1, mode_num + 1))]
            green_lens = [(int(x[0] * i / (mode_num + 1)) for i in reversed(range(1, mode_num + 1)))]
            simulator.simulate_preset(red_lens, green_lens, x[1:])
        return -simulator.get_reward()

    input_dim = 0
    domain = []
    if schedule_type == 'uniform':
        input_dim = 2
        domain = [{
            'name': 'red',
            'type': 'discrete',
            'domain': range(1, 60)
        }, {
            'name': 'green',
            'type': 'discrete',
            'domain': range(1, 60)
        }]
    elif schedule_type == 'distinct':
        input_dim = 2 * junction_num
        for i in range(junction_num):
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
    elif schedule_type == 'preset':
        input_dim = mode_num * 2 + junction_num
        for i in range(mode_num):
            domain.append({
                'name': f'red_{i}',
                'type': 'discrete',
                'domain': range(1, 60)
            })
        for i in range(mode_num):
            domain.append({
                'name': f'green_{i}',
                'type': 'discrete',
                'domain': range(1, 60)
            })
        for i in range(junction_num):
            domain.append({
                'name': f'mode_{i}',
                'type': 'discrete',
                'domain': range(0, mode_num)
            })
    elif schedule_type == 'forced_preset':
        input_dim = 1 + junction_num
        domain.append({
            'name': f'cycle_len',
            'type': 'discrete',
            'domain': range(0, 120)
        })
        for i in range(junction_num):
            domain.append({
                'name': f'mode_{i}',
                'type': 'discrete',
                'domain': range(0, mode_num)
            })

    kernel = GPy.kern.RBF(input_dim=input_dim, variance=1.0, lengthscale=4.0)
    opt = BayesianOptimization(f=lambda X: np.apply_along_axis(lambda x: f(x), 1, X),
                               domain=domain, model_type='GP', initial_design_numdata=1,
                               kernel=kernel, acquisition_type='EI')
    opt.run_optimization(max_iter=300)
    # opt.plot_acquisition()
    opt.plot_convergence()
    print(opt.x_opt)
    print(opt.fx_opt)

for schedule_type in schedule_options:
    optimize(schedule_type)
    if schedule_type in ['preset', 'forced_preset']:
        optimize(schedule_type, mode_num=4)
        optimize(schedule_type, mode_num=5)


