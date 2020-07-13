from plot_laplace_random_noise_values import laplace
from plot_gaussian_random_noise_values import gaussian
from receive_process_sensor_data_duplicate import create_utility_lists, plot_utility_graphs
from matplotlib import pyplot as plt

sensor_count_values = [5, 10, 15, 20, 25, 30, 35, 40, 45]
epsilon_values = [0.0, 0.5, 1.0, 1.5, 2.0]
distance_values_s_varying = [[119.07, 121.18, 120.72, 122.43, 121.16], 
                     [120.12, 122.43, 120.72, 122.42, 120.74, 120.74, 120.84, 120.74, 122.02, 121.16], 
                     [120.58, 122.04, 122.02, 121.18, 120.74, 121.59, 120.74, 120.74, 122.43, 122.85, 
                      122.85, 120.74, 121.99, 121.15, 122.01], 
                     [119.67, 121.54, 121.10, 121.54, 121.15, 120.70, 120.74, 120.70, 121.56, 120.39, 
                      121.15, 119.84, 121.15, 121.15, 120.29, 120.27, 121.99, 121.15, 120.38, 120.27], 
                     [120.55, 121.13, 120.70, 121.13, 120.29, 121.15, 121.15, 122.38, 122.40, 123.26, 
                     120.31, 122.01, 123.69, 121.59, 122.85, 121.15, 122.86, 123.69, 125.23, 122.43, 
                     121.59, 120.75, 120.74, 122.04, 121.18], 
                     [120.60, 120.74, 120.31, 121.15, 121.16, 120.74, 120.74, 120.31, 121.16, 122.01, 
                      120.72, 122.01, 121.59, 121.15, 122.74, 121.59, 121.59, 122.43, 121.16, 120.29, 
                      120.29, 120.31, 122.01, 122.01, 121.71, 120.74, 120.74, 121.27, 122.85, 121.15], 
                     [120.12, 121.15, 121.15, 121.15, 122.86, 121.16, 125.35, 121.16, 123.65, 120.70, 
                      121.15, 122.01, 122.01, 121.61, 124.51, 122.45, 123.69, 122.86, 121.27, 122.86, 
                      122.01, 122.45, 122.74, 120.72, 122.01, 120.31, 121.56, 122.81, 120.31, 120.75, 
                      121.15, 121.16, 121.15, 121.16, 121.59],
                     [122.26, 121.15, 120.72, 121.15, 121.13, 121.15, 121.15, 121.16, 121.15, 122.01, 
                      122.42, 121.15, 120.29, 121.25, 121.61, 122.86, 123.70, 120.39, 122.01, 121.59, 
                      120.32, 124.11, 120.70, 120.70, 120.70, 120.70, 121.15, 120.70, 122.81, 120.72, 
                      122.42, 121.56, 121.56, 123.65, 121.64, 120.70, 120.70, 120.80, 121.54, 122.40],
                     [120.56, 121.16, 121.15, 120.70, 121.15, 121.15, 124.11, 121.16, 121.16, 120.72, 
                      121.56, 121.16, 122.42, 120.70, 123.26, 123.26, 120.70, 120.26, 121.54, 121.54, 
                      120.26, 120.72, 122.40, 127.72, 120.82, 120.70, 121.16, 121.27, 125.37, 120.70, 
                      120.70, 122.40, 120.72, 122.40, 120.70, 120.70, 122.40, 122.40, 120.72, 120.70, 
                      120.70, 120.26, 120.70, 120.70, 121.54]]
distance_values_s_constant = [[120.56, 121.16, 121.15, 120.70, 121.15],
                     [120.56, 121.16, 121.15, 120.70, 121.15, 121.15, 124.11, 121.16, 121.16, 120.72],
                     [120.56, 121.16, 121.15, 120.70, 121.15, 121.15, 124.11, 121.16, 121.16, 120.72, 
                      121.56, 121.16, 122.42, 120.70, 123.26],
                     [120.56, 121.16, 121.15, 120.70, 121.15, 121.15, 124.11, 121.16, 121.16, 120.72, 
                      121.56, 121.16, 122.42, 120.70, 123.26, 123.26, 120.70, 120.26, 121.54, 121.54],
                     [120.56, 121.16, 121.15, 120.70, 121.15, 121.15, 124.11, 121.16, 121.16, 120.72, 
                      121.56, 121.16, 122.42, 120.70, 123.26, 123.26, 120.70, 120.26, 121.54, 121.54, 
                      120.26, 120.72, 122.40, 127.72, 120.82],
                     [120.56, 121.16, 121.15, 120.70, 121.15, 121.15, 124.11, 121.16, 121.16, 120.72, 
                      121.56, 121.16, 122.42, 120.70, 123.26, 123.26, 120.70, 120.26, 121.54, 121.54, 
                      120.26, 120.72, 122.40, 127.72, 120.82, 120.70, 121.16, 121.27, 125.37, 120.70],
                     [120.56, 121.16, 121.15, 120.70, 121.15, 121.15, 124.11, 121.16, 121.16, 120.72, 
                      121.56, 121.16, 122.42, 120.70, 123.26, 123.26, 120.70, 120.26, 121.54, 121.54, 
                      120.26, 120.72, 122.40, 127.72, 120.82, 120.70, 121.16, 121.27, 125.37, 120.70, 
                      120.70, 122.40, 120.72, 122.40, 120.70],
                     [120.56, 121.16, 121.15, 120.70, 121.15, 121.15, 124.11, 121.16, 121.16, 120.72, 
                      121.56, 121.16, 122.42, 120.70, 123.26, 123.26, 120.70, 120.26, 121.54, 121.54, 
                      120.26, 120.72, 122.40, 127.72, 120.82, 120.70, 121.16, 121.27, 125.37, 120.70, 
                      120.70, 122.40, 120.72, 122.40, 120.70, 120.70, 122.40, 122.40, 120.72, 120.70],
                     [120.56, 121.16, 121.15, 120.70, 121.15, 121.15, 124.11, 121.16, 121.16, 120.72, 
                      121.56, 121.16, 122.42, 120.70, 123.26, 123.26, 120.70, 120.26, 121.54, 121.54, 
                      120.26, 120.72, 122.40, 127.72, 120.82, 120.70, 121.16, 121.27, 125.37, 120.70, 
                      120.70, 122.40, 120.72, 122.40, 120.70, 120.70, 122.40, 122.40, 120.72, 120.70, 
                      120.70, 120.26, 120.70, 120.70, 121.54]]
distance_values_e = [[122.35, 120.79, 121.22, 122.47, 123.72, 120.34, 122.07, 120.79, 120.79, 120.79, 
                      122.47, 120.77, 121.23, 120.77, 124.18, 120.77, 121.23, 120.79, 121.23, 121.23, 
                      121.22, 121.64, 123.33, 121.20, 122.91, 122.91, 121.66, 120.91, 122.93, 120.38, 
                      122.91, 121.23, 121.23, 120.79, 120.79, 120.79, 122.49, 121.18, 121.63, 121.61, 
                      122.06, 122.47, 121.61, 121.63, 122.49], 
                     [120.32, 121.34, 120.32, 120.77, 121.73, 122.47, 121.64, 121.63, 120.34, 121.20, 
                      120.32, 120.79, 122.88, 120.77, 121.63, 122.88, 120.79, 122.88, 120.32, 121.59, 
                      121.18, 121.18, 121.18, 121.18, 120.44, 122.88, 120.77, 121.63, 121.63, 120.77, 
                      123.74, 121.28, 121.63, 126.24, 121.63, 121.63, 122.49, 121.63, 121.18, 122.49, 
                      122.07, 122.49, 121.64, 120.79, 123.33], 
                     [119.93, 120.79, 123.75, 120.80, 121.20, 120.44, 121.18, 120.34, 120.79, 122.50, 
                      121.22, 121.64, 121.64, 122.49, 121.64, 120.86, 122.49, 121.22, 121.63, 121.64, 
                      120.34, 121.20, 120.32, 122.90, 122.90, 122.90, 122.06, 121.20, 122.90, 121.64, 
                      122.90, 120.36, 121.63, 123.74, 120.79, 120.79, 120.91, 123.34, 123.34, 123.34, 
                      122.93, 122.49, 124.18, 122.49, 120.34], 
                     [120.34, 121.64, 121.64, 121.64, 122.90, 121.20, 121.20, 122.50, 122.88, 121.18, 
                      124.59, 121.30, 120.77, 121.18, 121.28, 121.20, 121.20, 123.74, 122.04, 122.49, 
                      122.90, 120.34, 120.77, 120.79, 121.66, 121.66, 121.64, 122.50, 122.50, 121.64, 
                      123.75, 122.52, 121.64, 124.11, 120.34, 121.64, 121.66, 123.75, 121.64, 121.66, 
                      121.64, 121.64, 120.79, 120.79, 121.20], 
                     [120.80, 121.64, 121.66, 120.80, 120.80, 121.23, 121.22, 123.36, 123.34, 121.32,  
                      122.50, 121.23, 122.09, 120.79, 120.80, 120.79, 120.79, 120.79, 120.34, 122.90, 
                      122.90, 120.79, 122.49, 122.49, 120.79, 121.64, 120.34, 122.90, 121.20, 121.20, 
                      122.90, 123.29, 121.64, 120.44, 123.31, 120.34, 121.20, 120.75, 120.75, 120.74, 
                      121.20, 122.06, 120.74, 122.06, 121.20]]

def calc_sum(list_of_values):
    sum_value = 0
    for i in range(0, len(list_of_values)):
        sum_value += list_of_values[i]
    return sum_value

if __name__ == '__main__':
    distance_values_s_noised_l = [[] for i in range(0, 9)]
    distance_values_s_noised_g = [[] for i in range(0, 9)]
    distance_values_e_noised_l = [[] for i in range(0, 5)]
    distance_values_e_noised_g = [[] for i in range(0, 5)]
    laplace_dist = []
    gaussian_dist = []
    distance_values_s = distance_values_s_constant
    for i in range(0, len(distance_values_s)):
        for j in range(0, len(distance_values_s[i])):
            noise = laplace(400.0 / 0.1)
            distance_values_s_noised_l[i].append(distance_values_s[i][j] + noise)
            laplace_dist.append(noise)
            noise = gaussian(0.0, (400.0 / 0.1))
            distance_values_s_noised_g[i].append(distance_values_s[i][j] + noise)
            gaussian_dist.append(noise)
        '''
        fig = plt.figure()
        plot = fig.add_subplot(111)
        plot.hist(laplace_dist)
        plt.show()
        fig = plt.figure()
        plot = fig.add_subplot(111)
        plot.hist(gaussian_dist)
        plt.show()
        '''
        laplace_dist.clear()
        gaussian_dist.clear()
    for i in range(0, len(distance_values_e)):
        for j in range(0, len(distance_values_e[i])):
            if epsilon_values[i] == 0.0:
                distance_values_e_noised_l[i].append(distance_values_e[i][j] + \
                        laplace(400.0 / 0.1))
                distance_values_e_noised_g[i].append(distance_values_e[i][j] + \
                        gaussian(0.0, (400.0 / 0.1)))
            else:
                distance_values_e_noised_l[i].append(distance_values_e[i][j] + \
                        laplace(400.0 / epsilon_values[i]))
                distance_values_e_noised_g[i].append(distance_values_e[i][j] + \
                        gaussian(0.0, (400.0 / epsilon_values[i])))
    print('distance_values_s_noised_l -> ' + str(distance_values_s_noised_l))
    print('distance_values_s_noised_g -> ' + str(distance_values_s_noised_g))
    print('distance_values_e_noised_l -> ' + str(distance_values_e_noised_l))
    print('distance_values_e_noised_g -> ' + str(distance_values_e_noised_g))
    distance_values = [[] for i in range(0, 5)]
    for i in range(0, len(sensor_count_values)):
            distance_values[0].append(calc_sum(distance_values_s[i]))
            distance_values[1].append(calc_sum(distance_values_s[i]) + \
                    laplace(400.0 / 0.1))
            distance_values[2].append(calc_sum(distance_values_s[i]) + \
                    gaussian(0.0, (400.0 / 0.1)))
            distance_values[3].append(calc_sum(distance_values_s_noised_l[i]))
            distance_values[4].append(calc_sum(distance_values_s_noised_g[i]))
    print('distance_values -> ' + str(distance_values))
    mape_util_l, mape_util_g, smape_util_l, smape_util_g, mmape_util_l, \
            mmape_util_g = create_utility_lists(distance_values)
    print('mape_util_l -> ' + str(mape_util_l))
    print('mape_util_g -> ' + str(mape_util_g))
    print('smape_util_l -> ' + str(smape_util_l))
    print('smape_util_g -> ' + str(smape_util_g))
    print('mmape_util_l -> ' + str(mmape_util_l))
    print('mmape_util_g -> ' + str(mmape_util_g))
    if None in mape_util_l[0] or None in mape_util_l[1] or \
            None in mape_util_g[0] or None in mape_util_g[1]:
                mape_util_l = None
                mape_util_g = None
    plot_utility_graphs(mape_util_l, mape_util_g, smape_util_l, smape_util_g, \
            mmape_util_l, mmape_util_g, sensor_count_values, 's', 'multiple')
    distance_values = [[] for i in range(0, 5)]
    for i in range(0, len(epsilon_values)):
            distance_values[0].append(calc_sum(distance_values_e[i]))
            if epsilon_values[i] == 0.0:
                distance_values[1].append(calc_sum(distance_values_e[i]) + \
                        laplace(400.0 / 0.1))
                distance_values[2].append(calc_sum(distance_values_e[i]) + \
                        gaussian(0.0, (400.0 / 0.1)))
            else:
                distance_values[1].append(calc_sum(distance_values_e[i]) + \
                        laplace(400.0 / epsilon_values[i]))
                distance_values[2].append(calc_sum(distance_values_e[i]) + \
                        gaussian(0.0, (400.0 / epsilon_values[i])))
            distance_values[3].append(calc_sum(distance_values_e_noised_l[i]))
            distance_values[4].append(calc_sum(distance_values_e_noised_g[i]))
    mape_util_l, mape_util_g, smape_util_l, smape_util_g, mmape_util_l, \
            mmape_util_g = create_utility_lists(distance_values)
    if None in mape_util_l[0] or None in mape_util_l[1] or \
            None in mape_util_g[0] or None in mape_util_g[1]:
                mape_util_l = None
                mape_util_g = None
    plot_utility_graphs(mape_util_l, mape_util_g, smape_util_l, smape_util_g, \
            mmape_util_l, mmape_util_g, epsilon_values, 'e', 'multiple') 
    print('Sum of constant and varying distance values, difference in sum of constant and varying distance values, absolute of sum of laplace and gaussian noise values, ratio of absolute sum of laplace and gaussian to sum of constant distance values, ratio of absolute sum of laplace and gaussian to sum of varying distance values')
    for i in range(0, len(distance_values_s)):
        print('{} sensors -> {}, {}, {}, {}, {}, {}, {}, {}, {}'.format( \
                str(sensor_count_values[i]), \
                str(calc_sum(distance_values_s_constant[i])), \
                str(calc_sum(distance_values_s_varying[i])), \
                str(abs(calc_sum(distance_values_s_constant[i]) - calc_sum(distance_values_s_varying[i]))), \
                str(abs(calc_sum(distance_values_s_noised_l[i]))), \
                str(abs(calc_sum(distance_values_s_noised_g[i]))), \
                str(abs(calc_sum(distance_values_s_noised_l[i]) / calc_sum(distance_values_s_constant[i]))), \
                str(abs(calc_sum(distance_values_s_noised_g[i]) / calc_sum(distance_values_s_constant[i]))), \
                str(abs(calc_sum(distance_values_s_noised_l[i]) / calc_sum(distance_values_s_varying[i]))), \
                str(abs(calc_sum(distance_values_s_noised_g[i]) / calc_sum(distance_values_s_varying[i])))))
