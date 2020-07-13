import matplotlib.pyplot as plt
import numpy as np
from math import log
from random import random, uniform, randint

def exp_sample(mean):
    return -mean * log(1.0 - random())

def randsign():
    value = randint(-1, 2)
    while value != -1 and value != 1:
        value = randint(-1, 2)
    return value

def laplace(scale):
    return exp_sample(scale) - exp_sample(scale)

'''
def laplace(scale):
    # value = random() - 0.5
    value = uniform(-0.5, 0.5)
    return scale * np.sign(value) * log(1 - 2 * abs(value))
'''

'''
def laplace(scale):
    return exp_sample(scale) * randsign()
'''

if __name__ == '__main__':
    with open('laplace_random_noise_values.txt', 'r') as f:
        laplace_random_noise_values = f.read().strip().split('\n\n')
    laplace_random_noise_values = ['0.0' if value == 'inf' or value == 'nan' \
            else value for value in laplace_random_noise_values]
    print(laplace_random_noise_values)
    # laplace_random_noise_values = []
    # for val in range(0, 500):
    #     laplace_random_noise_values.append(laplace(400.0 / 0.1))
    # print(laplace_random_noise_values)
    # laplace_random_noise_values = np.random.laplace(0.0, 400.0 / 0.1, (500, ))
    # print(laplace_random_noise_values)
    fig = plt.figure()
    plot = fig.add_subplot(111)
    # plot.plot(laplace_random_noise_values, \
    #         [val for val in range(0, len(laplace_random_noise_values))])
    # plot.bar(laplace_random_noise_values, \
    #         [val for val in range(0, len(laplace_random_noise_values))])
    plot.hist(laplace_random_noise_values)
    plt.show()
