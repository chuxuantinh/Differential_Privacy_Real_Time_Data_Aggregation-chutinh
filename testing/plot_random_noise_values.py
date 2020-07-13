import matplotlib.pyplot as plt
from math import sqrt
from random import random, uniform, randint, gauss, normalvariate
import sys

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: plot_random_noise_values.py <type>')
        sys.exit(0)
    with open('random_noise_values.txt', 'r') as f:
        random_noise_values = f.read().strip().split('\n\n')
    print(random_noise_values)
    # random_noise_values = []
    # rand_type = sys.argv[1]
    # for val in range(0, 500):
    #     if rand_type == 'random':
    #         random_noise_values.append(random())
    #     elif rand_type == 'uniform':
    #         random_noise_values.append(uniform(0.0, 500.0))
    #     elif rand_type == 'randint':
    #         random_noise_values.append(randint(0, 500))
    #     elif rand_type == 'gauss':
    #         # random_noise_values.append(gauss(0.0, (400.0 / 0.1) ** 0.5))
    #         random_noise_values.append(gauss(0.0, sqrt(400.0 / 0.1)))
    #     elif rand_type == 'normalvariate':
    #         # random_noise_values.append(normalvariate(0.0, (400.0 / 0.1) ** 0.5))
    #         random_noise_values.append(normalvariate(0.0, sqrt(400.0 / 0.1)))
    #     else:
    #         random_noise_values.append(0)
    # print(random_noise_values)
    fig = plt.figure()
    plot = fig.add_subplot(111)
    plot.hist(random_noise_values)
    plt.show()
