import matplotlib.pyplot as plt
import numpy as np
from math import cos, pi, sqrt, log
from random import random

def gaussian(mean, variance):
    r1 = random()
    r2 = random()
    return mean + variance * cos(2 * pi * r1) * sqrt(-log(r2))

if __name__ == '__main__':
    with open('gaussian_random_noise_values.txt', 'r') as f:
        gaussian_random_noise_values = f.read().strip().split('\n\n')
    gaussian_random_noise_values = ['0.0' if value == 'inf' or value == 'nan' \
            else value for value in gaussian_random_noise_values]
    print(gaussian_random_noise_values)
    # gaussian_random_noise_values = []
    # for val in range(0, 500):
    #     gaussian_random_noise_values.append(gaussian(0.0, (400.0 / 0.1)))
    # print(gaussian_random_noise_values)
    # gaussian_random_noise_values = np.random.normal(0.0, 400.0 / 0.1, (500, ))
    # print(gaussian_random_noise_values)
    fig = plt.figure()
    plot = fig.add_subplot(111)
    plot.hist(gaussian_random_noise_values)
    plt.show()
