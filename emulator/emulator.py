import numpy as np
import GPy
from GPyOpt.methods import BayesianOptimization

from simulator.simulator import Simulator

kernel = GPy.kern.RBF(input_dim=2, variance=1.0, lengthscale=4.0)

simulator = Simulator()
simulator.initialize_random_ring(junction_num=3, car_num=100)

def sim_and_reward(simulator, x):
    simulator.reset()
    simulator.simulate_uniform(x[0], x[1])
    return -simulator.get_reward()

domain = [
    {
        'name': 'red_len',
        'type': 'discrete',
        'domain': range(1, 60)
    },
    {
        'name': 'green_len',
        'type': 'discrete',
        'domain': range(1, 60)
    }
]

opt = BayesianOptimization(f=lambda X: np.apply_along_axis(
                                lambda x: sim_and_reward(simulator, x),
                           1, X),
                           domain=domain, model_type='GP',
                           initial_design_numdata=1,
                           kernel=kernel, acquisition_type='EI')
opt.run_optimization(max_iter=80)
opt.plot_acquisition()
opt.plot_convergence()
print(opt.x_opt)
print(opt.fx_opt)


opt_x = None
opt_reward = 0
for red_len in range(1, 60):
    for green_len in range(1, 60):
        reward = sim_and_reward(simulator, [red_len, green_len])
        if reward < opt_reward:
            opt_x = [red_len, green_len]
            opt_reward = reward
print(opt_x, opt_reward)