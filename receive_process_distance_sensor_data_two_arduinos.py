'''
This code is for collecting data upon uploading
ultrasonic_distance_sensor_dp_testing_multiple_blue/green_arduino codes to the Arduinos
and plotting utility, execution time and distance value graphs

Set DEBUG and INFO to 0,
CHGEPS to 1 and CHGSENSORCNT to 0 to vary epsilon,
CHGSENSORCNT to 1 and CHGEPS to 0 to vary sensor count,
CHGEPS to 0 and CHGSENSORCNT to 0 to vary nothing,
in the Arduino code before uploading and running this python code

Subsequently, this code expects two values i.e. sensitivity, epsilon/sensor
count, and then sets consisting of fourteen values i.e. sensor count/epsilon, 
original distance value post summation, distance value with laplace noise added
post summation, distance value with gaussian noise added post summation, dp 
noised distance values using laplace and gaussian post splitting post summation,
execution times for noise addition using laplace and gaussian before splitting,
for splitting, for noise addition after splitting, for partial summations, for
final summation and for the complete algorithm using laplace and gaussian, in 
that order
OR
it expects sixteen values i.e. sensitivity, epsilon, sensor count, original 
distance value post summation, distance value with laplace noise added post 
summation, distance value with gaussian noise added post summation and dp noised
distance values using laplace and gaussian post splitting post summation, 
execution times for noise addition using laplace and gaussian before splitting,
for splitting, for noise addition after splitting, for partial summations, for
final summation and for the complete algorithm using laplace and gaussian, in 
that order
'''

import serial
import serial.tools.list_ports
import serial.serialutil
import sys
import math
import argparse
import logging
import matplotlib.pyplot as plt
from math import log, cos, pi, sqrt
from random import random, randint
from multiprocessing import Process, Manager

'''
sensitivity, epsilon, sensor count
'''
num_of_constant_values = 3

num_of_distance_sum_values = 5
num_of_exec_time_values = 7
num_of_total_values = num_of_distance_sum_values + num_of_exec_time_values
min_epsilon = 0.0
max_epsilon = 2.0
epsilon_step = 0.5
min_sensor_count = 10
max_sensor_count = 90
sensor_count_step = 10

def exp_sample(mean):
    return -mean * log(1.0 - random())

def randsign():
    value = randint(-1, 2)
    while value != -1 and value != 1:
        value = randint(-1, 2)
    return value

def laplace(scale):
    return exp_sample(scale) - exp_sample(scale)

def gaussian(mean, variance):
    r1 = random()
    r2 = random()
    return mean + variance * cos(2 * pi * r1) * sqrt(-log(r2))

def setup_logging_config(log_level):
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logger = logging.getLogger()
    if log_level == 'debug':
        logger.setLevel(logging.DEBUG)
    elif log_level == 'info':
        logger.setLevel(logging.INFO)
    else:
        print('Correct log level not provided')
        sys.exit(0)
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s: %(message)s')
    file_handler = logging.FileHandler('distance_sensor_data.log', mode='a')
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

def setup_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vary-epsilon', '-ve', type=str, required=True, \
            help='pass yes/no for varying epsilon value')
    parser.add_argument('--vary-sensor-count', '-vscnt', type=str, \
            required=True, help='pass yes/no for varying sensor count')
    parser.add_argument('--plot-utility', '-pu', type=str, required=True, \
            help='pass yes/no to plot utility graphs')
    parser.add_argument('--plot-exectime', '-pe', type=str, required=True, \
            help='pass yes/no to plot execution time graphs')
    parser.add_argument('--plot-distance', '-pd', type=str, required=True, \
            help='pass yes/no to plot distance graphs')
    parser.add_argument('--plot-mode', '-pm', type=str, required=True, \
            help='pass single/multiple to plot graphs one per figure or group them to plot more than one per figure')
    parser.add_argument('--log-level', '-ll', type=str, required=True, \
            help='pass debug/info to set log level')
    parser.add_argument('--from-file', '-ff', type=str, required=True, \
            help='pass yes/no to use saved sensor values from a file or read new values from arduinos')
    return parser.parse_args()

def get_arduino_ports():
    arduino_ports = []
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if 'ACM' in port.device:
            arduino_ports.append(port.device)
    return arduino_ports

def get_data(process_num, return_dict, port, baudrate, timeout, mode, file_name):
    try:
        connection = serial.Serial(port, baudrate, timeout=timeout)
    except serial.serialutil.SerialException:
        logging.error('Connection cannot be established, port ' + port + ' busy')
        sys.exit(0)
    connection.isOpen()
    newline_count = 0
    if mode == 've':
        max_newline_count = (num_of_constant_values - 1) + \
                ((((max_epsilon - min_epsilon) / epsilon_step) + 1) * \
                (1 + (num_of_distance_sum_values - 2) + num_of_exec_time_values))
    elif mode == 'vscnt':
        max_newline_count = (num_of_constant_values - 1) + \
                (((((max_sensor_count / 2) - (min_sensor_count / 2)) / (sensor_count_step / 2)) + 1) * \
                (1 + (num_of_distance_sum_values - 2) + num_of_exec_time_values))
    elif mode == 'nochg':
        max_newline_count = num_of_constant_values + \
                (num_of_distance_sum_values - 2) + num_of_exec_time_values
    else:
        # return None
        return_dict[process_num] = None
    full_data = ''
    file_desc = open(file_name, 'w')
    while connection.isOpen() is True:
        try:
            data = connection.read().decode('utf-8')
            # print(data, end='', flush=True)
            print(data, end='', flush=True, file=file_desc)
            full_data += data
            if data == '\n':
                newline_count += 1
            if newline_count == max_newline_count:
                break
        except KeyboardInterrupt:
            connection.close()
            logging.error('Connection interrupted')
            sys.exit(0)
        except serial.serialutil.SerialException:
            connection.close()
            logging.error('Read failed')
            sys.exit(0)
    connection.close()
    file_desc.close()
    # return full_data
    return_dict[process_num] = full_data

def create_lists(data):
    epsilon_or_sensor_count_values = []
    distance_values = [[] for iterator in range(0, num_of_distance_sum_values - 2)]
    exec_times = [[] for iterator in range(0, num_of_exec_time_values)]
    for iterator in range(2, len(data)):
        if iterator % (num_of_total_values + 1 - 2) == 2:
            epsilon_or_sensor_count_values.append(data[iterator])
        elif iterator % (num_of_total_values + 1 - 2) == 3:
            distance_values[0].append(data[iterator])
        elif iterator % (num_of_total_values + 1 - 2) == 4:
            distance_values[1].append(data[iterator])
        elif iterator % (num_of_total_values + 1 - 2) == 5:
            distance_values[2].append(data[iterator])
        elif iterator % (num_of_total_values + 1 - 2) == 6:
            exec_times[0].append(data[iterator])
        elif iterator % (num_of_total_values + 1 - 2) == 7:
            exec_times[1].append(data[iterator])
        elif iterator % (num_of_total_values + 1 - 2) == 8:
            exec_times[2].append(data[iterator])
        elif iterator % (num_of_total_values + 1 - 2) == 9:
            exec_times[3].append(data[iterator])
        elif iterator % (num_of_total_values + 1 - 2) == 10:
            exec_times[4].append(data[iterator])
        elif iterator % (num_of_total_values + 1 - 2) == 0:
            exec_times[5].append(data[iterator])
        else:
            exec_times[6].append(data[iterator])
    epsilon_or_sensor_count_values = \
            [float(value) for value in epsilon_or_sensor_count_values]
    distance_values[0] = [float(value) for value in distance_values[0]]
    invalid_values = ['nan', 'ovf', 'inf']
    distance_values[1] = \
            [distance_values[0][iterator] if value in invalid_values else \
            float(value) for iterator, value in enumerate(distance_values[1])]
    distance_values[2] = \
            [distance_values[0][iterator] if value in invalid_values else \
            float(value) for iterator, value in enumerate(distance_values[2])]
    for iterator, value in enumerate(exec_times):
        exec_times[iterator] = [float(val) for val in exec_times[iterator]]
    return epsilon_or_sensor_count_values, distance_values, exec_times

def mape(old_value, new_value):
    if math.isclose(old_value, 0.0):
        return None
    else:
        return abs((old_value - new_value) / old_value)

def smape(old_value, new_value):
    return abs((old_value - new_value) / ((old_value + new_value) / 2))

def mmape(old_value, new_value):
    return abs((old_value - new_value) / (old_value + 1))

def create_utility_lists(distance_values):
    mape_util_laplace = [[] for iterator in range(0, 2)]
    mape_util_gaussian = [[] for iterator in range(0, 2)]
    smape_util_laplace = [[] for iterator in range(0, 2)]
    smape_util_gaussian = [[] for iterator in range(0, 2)]
    mmape_util_laplace = [[] for iterator in range(0, 2)]
    mmape_util_gaussian = [[] for iterator in range(0, 2)]
    for iterator in range(0, len(distance_values[0])):
        mape_util_laplace[0].append(mape(distance_values[0][iterator], \
                distance_values[1][iterator]))
        mape_util_laplace[1].append(mape(distance_values[0][iterator], \
                distance_values[3][iterator]))
        mape_util_gaussian[0].append(mape(distance_values[0][iterator], \
                distance_values[2][iterator]))
        mape_util_gaussian[1].append(mape(distance_values[0][iterator], \
                distance_values[4][iterator]))
        smape_util_laplace[0].append(mape(distance_values[0][iterator], \
                distance_values[1][iterator]))
        smape_util_laplace[1].append(mape(distance_values[0][iterator], \
                distance_values[3][iterator]))
        smape_util_gaussian[0].append(mape(distance_values[0][iterator], \
                distance_values[2][iterator]))
        smape_util_gaussian[1].append(mape(distance_values[0][iterator], \
                distance_values[4][iterator]))
        mmape_util_laplace[0].append(mape(distance_values[0][iterator], \
                distance_values[1][iterator]))
        mmape_util_laplace[1].append(mape(distance_values[0][iterator], \
                distance_values[3][iterator]))
        mmape_util_gaussian[0].append(mape(distance_values[0][iterator], \
                distance_values[2][iterator]))
        mmape_util_gaussian[1].append(mape(distance_values[0][iterator], \
                distance_values[4][iterator]))
    return mape_util_laplace, mape_util_gaussian, \
            smape_util_laplace, smape_util_gaussian, \
            mmape_util_laplace, mmape_util_gaussian

def create_plot_single():
    fig = plt.figure(figsize=(14, 10))
    fig.subplots_adjust(bottom=0.25)
    return fig, fig.add_subplot(111)

def plot_line_graphs(util_type, x_axis_values, \
        util_laplace, util_gaussian, x_axis, ylabel, title):
    util_type.plot(x_axis_values, util_laplace[0], 'bo-', \
            label='central method using laplace')
    util_type.plot(x_axis_values, util_gaussian[0], 'rs-', \
            label='central method using gaussian')
    util_type.plot(x_axis_values, util_laplace[1], 'g^-', \
            label='split method using laplace')
    util_type.plot(x_axis_values, util_gaussian[1], 'yx-', \
            label='split method using gaussian')
    if x_axis == 'e':
        util_type.set_xlabel('epsilon value')
    elif x_axis == 's':
        util_type.set_xlabel('number of sensors')
    else:
        logging.error('Correct option for x-axis not provided to plot graphs')
        sys.exit(0)
    util_type.set_ylabel(ylabel)
    util_type.set_title(title, loc='center', fontweight='bold')

def plot_utility_graphs(mape_util_laplace, mape_util_gaussian, \
        smape_util_laplace, smape_util_gaussian, \
        mmape_util_laplace, mmape_util_gaussian, x_axis_values, x_axis, \
        plot_mode):
    '''
    graph 1 -> utility in MAPE vs number of sensors / epsilon
            -> central method - laplace and gaussian
            -> split method - laplace and gaussian
    graph 2 -> utility in SMAPE vs number of sensors / epsilon
            -> central method - laplace and gaussian
            -> split method - laplace and gaussian
    graph 3 -> utility in MMAPE vs number of sensors / epsilon
            -> central method - laplace and gaussian
            -> split method - laplace and gaussian
    graph 4 -> utility in log(MMAPE) vs number of sensors / epsilon
            -> central method - laplace and gaussian
            -> split method - laplace and gaussian
    '''
    if plot_mode == 'single':
        if mape_util_laplace is None or mape_util_gaussian is None:
            fig, smape = create_plot_single()
            plot_line_graphs(smape, x_axis_values, \
                    smape_util_laplace, smape_util_gaussian, x_axis, \
                    'utility in SMAPE', 'SMAPE utility')
            handles, labels = smape.get_legend_handles_labels()
            fig.legend(handles, labels, loc='lower center')
            if x_axis == 'e':
                plt.savefig('plots/changing_epsilon/single/utility_graph_smape.png', \
                        bbox_inches='tight')
            elif x_axis == 's':
                plt.savefig('plots/changing_sensor_count/single/utility_graph_smape.png', \
                        bbox_inches='tight')
            else:
                logging.error('Correct option for x-axis not provided to plot graphs')
                sys.exit(0)
            plt.show()
            fig, mmape = create_plot_single()
            plot_line_graphs(mmape, x_axis_values, \
                    mmape_util_laplace, mmape_util_gaussian, x_axis, \
                    'utility in MMAPE', 'MAPE utility')
            handles, labels = mmape.get_legend_handles_labels()
            fig.legend(handles, labels, loc='lower center')
            if x_axis == 'e':
                plt.savefig('plots/changing_epsilon/single/utility_graph_mmape.png', \
                        bbox_inches='tight')
            elif x_axis == 's':
                plt.savefig('plots/changing_sensor_count/single/utility_graph_mmape.png', \
                        bbox_inches='tight')
            else:
                logging.error('Correct option for x-axis not provided to plot graphs')
                sys.exit(0)
            plt.show()
            fig, log_mmape = create_plot_single()
            plot_line_graphs(log_mmape, x_axis_values, \
                [[math.log(value) if value != 0.0 else 0.0 \
                for value in mmape_util_laplace[0]], \
                [math.log(value) if value != 0.0 else 0.0 \
                for value in mmape_util_laplace[1]]], \
                [[math.log(value) if value != 0.0 else 0.0 \
                for value in mmape_util_gaussian[0]], \
                [math.log(value) if value != 0.0 else 0.0 \
                for value in mmape_util_gaussian[1]]], \
                x_axis, 'utility in log(MMAPE)', 'MMAPE utility')
            handles, labels = log_mmape.get_legend_handles_labels()
            fig.legend(handles, labels, loc='lower center')
            if x_axis == 'e':
                plt.savefig('plots/changing_epsilon/single/utility_graph_log_mmape.png', \
                        bbox_inches='tight')
            elif x_axis == 's':
                plt.savefig('plots/changing_sensor_count/single/utility_graph_log_mmape.png', \
                        bbox_inches='tight')
            else:
                logging.error('Correct option for x-axis not provided to plot graphs')
                sys.exit(0)
            plt.show()
        else:
            fig, mape = create_plot_single()
            plot_line_graphs(mape, x_axis_values, \
                    mape_util_laplace, mape_util_gaussian, x_axis, \
                    'utility in MAPE', 'MAPE utility')
            handles, labels = mape.get_legend_handles_labels()
            fig.legend(handles, labels, loc='lower center')
            if x_axis == 'e':
                plt.savefig('plots/changing_epsilon/single/utility_graph_mape.png', \
                        bbox_inches='tight')
            elif x_axis == 's':
                plt.savefig('plots/changing_sensor_count/single/utility_graph_mape.png', \
                        bbox_inches='tight')
            else:
                logging.error('Correct option for x-axis not provided to plot graphs')
                sys.exit(0)
            plt.show()
            fig, smape = create_plot_single()
            plot_line_graphs(smape, x_axis_values, \
                    smape_util_laplace, smape_util_gaussian, x_axis, \
                    'utility in SMAPE', 'SMAPE utility')
            handles, labels = smape.get_legend_handles_labels()
            fig.legend(handles, labels, loc='lower center')
            if x_axis == 'e':
                plt.savefig('plots/changing_epsilon/single/utility_graph_smape.png', \
                        bbox_inches='tight')
            elif x_axis == 's':
                plt.savefig('plots/changing_sensor_count/single/utility_graph_smape.png', \
                        bbox_inches='tight')
            else:
                logging.error('Correct option for x-axis not provided to plot graphs')
                sys.exit(0)
            plt.show()
            fig, mmape = create_plot_single()
            plot_line_graphs(mmape, x_axis_values, \
                    mmape_util_laplace, mmape_util_gaussian, x_axis, \
                    'utility in MMAPE', 'MMAPE utility')
            handles, labels = mmape.get_legend_handles_labels()
            fig.legend(handles, labels, loc='lower center')
            if x_axis == 'e':
                plt.savefig('plots/changing_epsilon/single/utility_graph_mmape.png', \
                        bbox_inches='tight')
            elif x_axis == 's':
                plt.savefig('plots/changing_sensor_count/single/utility_graph_mmape.png', \
                        bbox_inches='tight')
            else:
                logging.error('Correct option for x-axis not provided to plot graphs')
                sys.exit(0)
            plt.show()
            fig, log_mmape = create_plot_single()
            plot_line_graphs(log_mmape, x_axis_values, \
                [[math.log(value) if value != 0.0 else 0.0 \
                for value in mmape_util_laplace[0]], \
                [math.log(value) if value != 0.0 else 0.0 \
                for value in mmape_util_laplace[1]]], \
                [[math.log(value) if value != 0.0 else 0.0 \
                for value in mmape_util_gaussian[0]], \
                [math.log(value) if value != 0.0 else 0.0 \
                for value in mmape_util_gaussian[1]]], \
                x_axis, 'utility in log(MMAPE)', 'MMAPE utility')
            handles, labels = log_mmape.get_legend_handles_labels()
            fig.legend(handles, labels, loc='lower center')
            if x_axis == 'e':
                plt.savefig('plots/changing_epsilon/single/utility_graph_log_mmape.png', \
                        bbox_inches='tight')
            elif x_axis == 's':
                plt.savefig('plots/changing_sensor_count/single/utility_graph_log_mmape.png', \
                        bbox_inches='tight')
            else:
                logging.error('Correct option for x-axis not provided to plot graphs')
                sys.exit(0)
            plt.show()
    elif plot_mode == 'multiple':
        fig = plt.figure(figsize=(14, 10))
        fig.subplots_adjust(bottom=0.2, wspace=0.6, hspace=0.6)
        if mape_util_laplace is None or mape_util_gaussian is None:
            smape = fig.add_subplot(221)
            plot_line_graphs(smape, x_axis_values, \
                    smape_util_laplace, smape_util_gaussian, x_axis, \
                    'utility in SMAPE', 'SMAPE utility')
            mmape = fig.add_subplot(222)
            plot_line_graphs(mmape, x_axis_values, \
                    mmape_util_laplace, mmape_util_gaussian, x_axis, \
                    'utility in MMAPE', 'MMAPE utility')
            log_mmape = fig.add_subplot(223)
            plot_line_graphs(log_mmape, x_axis_values, \
                [[math.log(value) if value != 0.0 else 0.0 \
                for value in mmape_util_laplace[0]], \
                [math.log(value) if value != 0.0 else 0.0 \
                for value in mmape_util_laplace[1]]], \
                [[math.log(value) if value != 0.0 else 0.0 \
                for value in mmape_util_gaussian[0]], \
                [math.log(value) if value != 0.0 else 0.0 \
                for value in mmape_util_gaussian[1]]], \
                x_axis, 'utility in log(MMAPE)', 'MMAPE utility')
            handles, labels = smape.get_legend_handles_labels()
        else:
            mape = fig.add_subplot(221)
            plot_line_graphs(mape, x_axis_values, \
                    mape_util_laplace, mape_util_gaussian, x_axis, \
                    'utility in MAPE', 'MAPE utility')
            smape = fig.add_subplot(222)
            plot_line_graphs(smape, x_axis_values, \
                    smape_util_laplace, smape_util_gaussian, x_axis, \
                    'utility in SMAPE', 'SMAPE utility')
            mmape = fig.add_subplot(223)
            plot_line_graphs(mmape, x_axis_values, \
                    mmape_util_laplace, mmape_util_gaussian, x_axis, \
                    'utility in MMAPE', 'MMAPE utility')
            log_mmape = fig.add_subplot(224)
            plot_line_graphs(log_mmape, x_axis_values, \
                [[math.log(value) if value != 0.0 else 0.0 \
                for value in mmape_util_laplace[0]], \
                [math.log(value) if value != 0.0 else 0.0 \
                for value in mmape_util_laplace[1]]], \
                [[math.log(value) if value != 0.0 else 0.0 \
                for value in mmape_util_gaussian[0]], \
                [math.log(value) if value != 0.0 else 0.0 \
                for value in mmape_util_gaussian[1]]], \
                x_axis, 'utility in log(MMAPE)', 'MMAPE utility')
            handles, labels = mape.get_legend_handles_labels()
        fig.legend(handles, labels, loc='lower center')
        if x_axis == 'e':
            plt.savefig('plots/changing_epsilon/multiple/utility_graphs.png', \
                    bbox_inches='tight')
        elif x_axis == 's':
            plt.savefig('plots/changing_sensor_count/multiple/utility_graphs.png', \
                    bbox_inches='tight')
        else:
            logging.error('Correct option for x-axis not provided to plot graphs')
            sys.exit(0)
        plt.show()
    else:
        logging.error('Correct option for plot mode not provided to plot graphs')
        sys.exit(0)

def plot_exec_time_graphs(exec_times, x_axis_values, x_axis, plot_mode):
    '''
    graph 1 -> execution time in microseconds vs number of sensors / epsilon
            -> noise addition before splitting - laplace and gaussian
    graph 2 -> execution time in microseconds vs number of sensors / epsilon
            -> for splitting
    graph 3 -> execution time in microseconds vs number of sensors / epsilon
            -> noise addition after splitting
    graph 4 -> execution time in microseconds vs number of sensors / epsilon
            -> for partial summations
    graph 5 -> execution time in microseconds vs number of sensors / epsilon
            -> complete algorithm - laplace and gaussian
    '''
    if len(x_axis_values) == (max_epsilon / epsilon_step) + 1:
        width = 0.1
    elif len(x_axis_values) == max_sensor_count / sensor_count_step:
        width = 1.25
    else:
        width = 0.75
    if plot_mode == 'single':
        fig, exec_time_noise_add_before_split = create_plot_single()
        exec_time_noise_add_before_split.bar(x_axis_values, exec_times[0], \
                width=-width, color='b', align='edge')
        exec_time_noise_add_before_split.bar(x_axis_values, exec_times[1], \
                width=width, color='r', align='edge')
        if x_axis == 'e':
            exec_time_noise_add_before_split.set_xlabel('epsilon value')
        elif x_axis == 's':
            exec_time_noise_add_before_split.set_xlabel('number of sensors')
        else:
            logging.error('Correct option for x-axis not provided to plot graphs')
            sys.exit(0)
        exec_time_noise_add_before_split.set_ylabel('execution time\nin microseconds')
        exec_time_noise_add_before_split.set_title('Execution time\nfor noise addition before splitting', \
                loc='center', pad=20, fontweight='bold')
        fig.legend(labels=['laplace', 'gaussian'], loc='lower center')
        if x_axis == 'e':
            plt.savefig('plots/changing_epsilon/single/exec_time_graph_noise_add_before_split.png', \
                    bbox_inches='tight')
        elif x_axis == 's':
            plt.savefig('plots/changing_sensor_count/single/exec_time_graph_noise_add_before_split.png', \
                    bbox_inches='tight')
        else:
            logging.error('Correct option for x-axis not provided to plot graphs')
            sys.exit(0)
        plt.show()
        fig, exec_time_for_split = create_plot_single()
        exec_time_for_split.bar(x_axis_values, exec_times[2], \
                width=width, color='g', align='center')
        if x_axis == 'e':
            exec_time_for_split.set_xlabel('epsilon value')
        elif x_axis == 's':
            exec_time_for_split.set_xlabel('number of sensors')
        else:
            logging.error('Correct option for x-axis not provided to plot graphs')
            sys.exit(0)
        exec_time_for_split.set_ylabel('execution time\nin microseconds')
        exec_time_for_split.set_title('Execution time\nfor splitting', \
                loc='center', pad=20, fontweight='bold')
        fig.legend(labels=['irrespective of laplace or gaussian'], loc='lower center')
        if x_axis == 'e':
            plt.savefig('plots/changing_epsilon/single/exec_time_graph_for_split.png', \
                    bbox_inches='tight')
        elif x_axis == 's':
            plt.savefig('plots/changing_sensor_count/single/exec_time_graph_for_split.png', \
                    bbox_inches='tight')
        else:
            logging.error('Correct option for x-axis not provided to plot graphs')
            sys.exit(0)
        plt.show()
        fig, exec_time_noise_add_after_split = create_plot_single()
        exec_time_noise_add_after_split.bar(x_axis_values, exec_times[3], \
                width=width, color='g', align='center')
        if x_axis == 'e':
            exec_time_noise_add_after_split.set_xlabel('epsilon value')
        elif x_axis == 's':
            exec_time_noise_add_after_split.set_xlabel('number of sensors')
        else:
            logging.error('Correct option for x-axis not provided to plot graphs')
            sys.exit(0)
        exec_time_noise_add_after_split.set_ylabel('execution time\nin microseconds')
        exec_time_noise_add_after_split.set_title('Execution time\nfor noise addition after splitting', \
                loc='center', pad=20, fontweight='bold')
        fig.legend(labels=['irrespective of laplace or gaussian'], loc='lower center')
        if x_axis == 'e':
            plt.savefig('plots/changing_epsilon/single/exec_time_graph_noise_add_after_split.png', \
                    bbox_inches='tight')
        elif x_axis == 's':
            plt.savefig('plots/changing_sensor_count/single/exec_time_graph_noise_add_after_split.png', \
                    bbox_inches='tight')
        else:
            logging.error('Correct option for x-axis not provided to plot graphs')
            sys.exit(0)
        plt.show()
        fig, exec_time_for_partial_summations = create_plot_single()
        exec_time_for_partial_summations.bar(x_axis_values, exec_times[4], \
                width=width, color='g', align='center')
        if x_axis == 'e':
            exec_time_for_partial_summations.set_xlabel('epsilon value')
        elif x_axis == 's':
            exec_time_for_partial_summations.set_xlabel('number of sensors')
        else:
            logging.error('Correct option for x-axis not provided to plot graphs')
            sys.exit(0)
        exec_time_for_partial_summations.set_ylabel('execution time\nin microseconds')
        exec_time_for_partial_summations.set_title('Execution time\nfor partial summations', \
                loc='center', pad=20, fontweight='bold')
        fig.legend(labels=['irrespective of laplace or gaussian'], loc='lower center')
        if x_axis == 'e':
            plt.savefig('plots/changing_epsilon/single/exec_time_graph_for_partial_summations.png', \
                    bbox_inches='tight')
        elif x_axis == 's':
            plt.savefig('plots/changing_sensor_count/single/exec_time_graph_for_partial_summations.png', \
                    bbox_inches='tight')
        else:
            logging.error('Correct option for x-axis not provided to plot graphs')
            sys.exit(0)
        plt.show()
        fig, exec_time_complete_algorithm = create_plot_single()
        exec_time_complete_algorithm.bar(x_axis_values, exec_times[5], \
                width=-width, color='b', align='edge')
        exec_time_complete_algorithm.bar(x_axis_values, exec_times[6], \
                width=width, color='r', align='edge')
        if x_axis == 'e':
            exec_time_complete_algorithm.set_xlabel('epsilon value')
        elif x_axis == 's':
            exec_time_complete_algorithm.set_xlabel('number of sensors')
        else:
            logging.error('Correct option for x-axis not provided to plot graphs')
            sys.exit(0)
        exec_time_complete_algorithm.set_ylabel('execution time\nin microseconds')
        exec_time_complete_algorithm.set_title('Execution time\nfor complete algorithm', \
                loc='center', pad=20, fontweight='bold')
        fig.legend(labels=['laplace', 'gaussian'], loc='lower center')
        if x_axis == 'e':
            plt.savefig('plots/changing_epsilon/single/exec_time_graph_complete_algorithm.png', \
                    bbox_inches='tight')
        elif x_axis == 's':
            plt.savefig('plots/changing_sensor_count/single/exec_time_graph_complete_algorithm.png', \
                    bbox_inches='tight')
        else:
            logging.error('Correct option for x-axis not provided to plot graphs')
            sys.exit(0)
        plt.show()
    elif plot_mode == 'multiple':
        fig = plt.figure(figsize=(14, 10))
        fig.subplots_adjust(bottom=0.15, wspace=0.6, hspace=0.8)
        exec_time_noise_add_before_split = fig.add_subplot(231)
        exec_time_noise_add_before_split.bar(x_axis_values, exec_times[0], \
                width=-width, color='b', align='edge')
        exec_time_noise_add_before_split.bar(x_axis_values, exec_times[1], \
                width=width, color='r', align='edge')
        if x_axis == 'e':
            exec_time_noise_add_before_split.set_xlabel('epsilon value')
        elif x_axis == 's':
            exec_time_noise_add_before_split.set_xlabel('number of sensors')
        else:
            logging.error('Correct option for x-axis not provided to plot graphs')
            sys.exit(0)
        exec_time_noise_add_before_split.set_ylabel('execution time\nin microseconds')
        exec_time_noise_add_before_split.set_title('Execution time\nfor noise addition before splitting', \
                loc='center', pad=20, fontweight='bold')
        exec_time_for_split = fig.add_subplot(232)
        exec_time_for_split.bar(x_axis_values, exec_times[2], \
                width=width, color='g', align='center')
        if x_axis == 'e':
            exec_time_for_split.set_xlabel('epsilon value')
        elif x_axis == 's':
            exec_time_for_split.set_xlabel('number of sensors')
        else:
            logging.error('Correct option for x-axis not provided to plot graphs')
            sys.exit(0)
        exec_time_for_split.set_ylabel('execution time\nin microseconds')
        exec_time_for_split.set_title('Execution time\nfor splitting', \
                loc='center', pad=20, fontweight='bold')
        exec_time_noise_add_after_split = fig.add_subplot(233)
        exec_time_noise_add_after_split.bar(x_axis_values, exec_times[3], \
                width=width, color='g', align='center')
        if x_axis == 'e':
            exec_time_noise_add_after_split.set_xlabel('epsilon value')
        elif x_axis == 's':
            exec_time_noise_add_after_split.set_xlabel('number of sensors')
        else:
            logging.error('Correct option for x-axis not provided to plot graphs')
            sys.exit(0)
        exec_time_noise_add_after_split.set_ylabel('execution time\nin microseconds')
        exec_time_noise_add_after_split.set_title('Execution time\nfor noise addition after splitting', \
                loc='center', pad=20, fontweight='bold')
        exec_time_for_partial_summations = fig.add_subplot(234)
        exec_time_for_partial_summations.bar(x_axis_values, exec_times[4], \
                width=width, color='g', align='center')
        if x_axis == 'e':
            exec_time_for_partial_summations.set_xlabel('epsilon value')
        elif x_axis == 's':
            exec_time_for_partial_summations.set_xlabel('number of sensors')
        else:
            logging.error('Correct option for x-axis not provided to plot graphs')
            sys.exit(0)
        exec_time_for_partial_summations.set_ylabel('execution time\nin microseconds')
        exec_time_for_partial_summations.set_title('Execution time\nfor partial summations', \
                loc='center', pad=20, fontweight='bold')
        exec_time_complete_algorithm = fig.add_subplot(235)
        exec_time_complete_algorithm.bar(x_axis_values, exec_times[5], \
                width=-width, color='b', align='edge')
        exec_time_complete_algorithm.bar(x_axis_values, exec_times[6], \
                width=width, color='r', align='edge')
        if x_axis == 'e':
            exec_time_complete_algorithm.set_xlabel('epsilon value')
        elif x_axis == 's':
            exec_time_complete_algorithm.set_xlabel('number of sensors')
        else:
            logging.error('Correct option for x-axis not provided to plot graphs')
            sys.exit(0)
        exec_time_complete_algorithm.set_ylabel('execution time\nin microseconds')
        exec_time_complete_algorithm.set_title('Execution time\nfor complete algorithm', \
                loc='center', pad=20, fontweight='bold')
        fig.legend(labels=['laplace', 'gaussian'], loc='lower center')
        if x_axis == 'e':
            plt.savefig('plots/changing_epsilon/multiple/exec_time_graphs.png', \
                    bbox_inches='tight')
        elif x_axis == 's':
            plt.savefig('plots/changing_sensor_count/multiple/exec_time_graphs.png', \
                    bbox_inches='tight')
        else:
            logging.error('Correct option for x-axis not provided to plot graphs')
            sys.exit(0)
        plt.show()
    else:
        logging.error('Correct option for plot mode not provided to plot graphs')
        sys.exit(0)
    '''
    graph 1 -> difference in execution time in microseconds vs number of 
                sensors / epsilon
            -> noise addition before splitting - laplace and gaussian
    graph 2 -> difference in execution time in microseconds vs number of 
                sensors / epsilon
            -> for splitting
    graph 3 -> difference in execution time in microseconds vs number of 
                sensors / epsilon
            -> noise addition after splitting
    graph 4 -> difference in execution time in microseconds vs number of 
                sensors / epsilon
            -> for partial summations
    graph 5 -> difference in execution time in microseconds vs number of 
                sensors / epsilon
            -> complete algorithm - laplace and gaussian
    '''
    if len(x_axis_values) == max_sensor_count / sensor_count_step:
        noise_add_before_split_gaussian_time_diff = [value if iterator == 0 \
                else value - exec_times[0][iterator - 1] for iterator, value \
                in enumerate(exec_times[0])][1:]
        noise_add_before_split_laplace_time_diff = [value if iterator == 0 \
                else value - exec_times[1][iterator - 1] for iterator, value \
                in enumerate(exec_times[1])][1:]
        for_split_time_diff = [value if iterator == 0 \
                else value - exec_times[2][iterator - 1] for iterator, value \
                in enumerate(exec_times[2])][1:]
        noise_add_after_split_time_diff = [value if iterator == 0 \
                else value - exec_times[3][iterator - 1] for iterator, value \
                in enumerate(exec_times[3])][1:]
        for_partial_summations_time_diff = [value if iterator == 0 \
                else value - exec_times[4][iterator - 1] for iterator, value \
                in enumerate(exec_times[4])][1:]
        complete_algorithm_gaussian_time_diff = [value if iterator == 0 \
                else value - exec_times[5][iterator - 1] for iterator, value \
                in enumerate(exec_times[5])][1:]
        complete_algorithm_laplace_time_diff = [value if iterator == 0 \
                else value - exec_times[6][iterator - 1] for iterator, value \
                in enumerate(exec_times[6])][1:]
        width = 0.3
        x_axis_values = ['0' + '-' + str(value) if iterator == 0 \
                else str(x_axis_values[iterator - 1]) + '-' + str(value) \
                for iterator, value in enumerate(x_axis_values)][1:]
        if plot_mode == 'single':
            fig, time_diff_noise_add_before_split = create_plot_single()
            time_diff_noise_add_before_split.bar(x_axis_values, \
                    noise_add_before_split_gaussian_time_diff, \
                    width=-width, color='b', align='edge')
            time_diff_noise_add_before_split.bar(x_axis_values, \
                    noise_add_before_split_laplace_time_diff, \
                    width=width, color='r', align='edge')
            if x_axis == 's':
                time_diff_noise_add_before_split.set_xlabel('change in number of sensors')
                time_diff_noise_add_before_split.set_xticklabels(x_axis_values, \
                        rotation=(45))
            else:
                logging.error('Correct option for x-axis not provided to plot graphs')
                sys.exit(0)
            time_diff_noise_add_before_split.set_ylabel('difference in execution time\nin microseconds')
            time_diff_noise_add_before_split.set_title('Difference in execution time\nfor noise addition before splitting', \
                    loc='center', pad=10, fontsize=10, fontweight='bold')
            fig.legend(labels=['laplace', 'gaussian'], loc='lower center')
            if x_axis == 's':
                plt.savefig('plots/changing_sensor_count/single/exec_time_difference_graph_noise_add_before_split.png', \
                        bbox_inches='tight')
            else:
                logging.error('Correct option for x-axis not provided to plot graphs')
                sys.exit(0)
            plt.show()
            fig, time_diff_for_split = create_plot_single()
            time_diff_for_split.bar(x_axis_values, for_split_time_diff, \
                    width=width, color='g', align='center')
            if x_axis == 's':
                time_diff_for_split.set_xlabel('change in number of sensors')
                time_diff_for_split.set_xticklabels(x_axis_values, rotation=(45))
            else:
                logging.error('Correct option for x-axis not provided to plot graphs')
                sys.exit(0)
            time_diff_for_split.set_ylabel('difference in execution time\nin microseconds')
            time_diff_for_split.set_title('Difference in execution time\nfor splitting', \
                    loc='center', pad=10, fontsize=10, fontweight='bold')
            fig.legend(labels=['irrespective of laplace or gaussian'], loc='lower center')
            if x_axis == 's':
                plt.savefig('plots/changing_sensor_count/single/exec_time_difference_graph_for_split.png', \
                        bbox_inches='tight')
            else:
                logging.error('Correct option for x-axis not provided to plot graphs')
                sys.exit(0)
            plt.show()
            fig, time_diff_noise_add_after_split = create_plot_single()
            time_diff_noise_add_after_split.bar(x_axis_values, \
                    noise_add_after_split_time_diff, \
                    width=width, color='g', align='center')
            if x_axis == 's':
                time_diff_noise_add_after_split.set_xlabel('change in number of sensors')
                time_diff_noise_add_after_split.set_xticklabels(x_axis_values, \
                        rotation=(45))
            else:
                logging.error('Correct option for x-axis not provided to plot graphs')
                sys.exit(0)
            time_diff_noise_add_after_split.set_ylabel('difference in execution time\nin microseconds')
            time_diff_noise_add_after_split.set_title('Difference in execution time\nfor noise addition after splitting', \
                    loc='center', pad=10, fontsize=10, fontweight='bold')
            fig.legend(labels=['irrespective of laplace or gaussian'], loc='lower center')
            if x_axis == 's':
                plt.savefig('plots/changing_sensor_count/single/exec_time_difference_graph_noise_add_after_split.png', \
                        bbox_inches='tight')
            else:
                logging.error('Correct option for x-axis not provided to plot graphs')
                sys.exit(0)
            plt.show()
            fig, time_diff_for_partial_summations = create_plot_single()
            time_diff_for_partial_summations.bar(x_axis_values, \
                    for_partial_summations_time_diff, \
                    width=width, color='g', align='center')
            if x_axis == 's':
                time_diff_for_partial_summations.set_xlabel('change in number of sensors')
                time_diff_for_partial_summations.set_xticklabels(x_axis_values, rotation=(45))
            else:
                logging.error('Correct option for x-axis not provided to plot graphs')
                sys.exit(0)
            time_diff_for_partial_summations.set_ylabel('difference in execution time\nin microseconds')
            time_diff_for_partial_summations.set_title('Difference in execution time\nfor partial summations', \
                    loc='center', pad=10, fontsize=10, fontweight='bold')
            fig.legend(labels=['irrespective of laplace or gaussian'], loc='lower center')
            if x_axis == 's':
                plt.savefig('plots/changing_sensor_count/single/exec_time_difference_graph_for_partial_summations.png', \
                        bbox_inches='tight')
            else:
                logging.error('Correct option for x-axis not provided to plot graphs')
                sys.exit(0)
            plt.show()
            fig, time_diff_complete_algorithm = create_plot_single()
            time_diff_complete_algorithm.bar(x_axis_values, \
                    complete_algorithm_laplace_time_diff, \
                    width=-width, color='b', align='edge')
            time_diff_complete_algorithm.bar(x_axis_values, \
                    complete_algorithm_gaussian_time_diff, \
                    width=width, color='r', align='edge')
            if x_axis == 's':
                time_diff_complete_algorithm.set_xlabel('change in number of sensors')
                time_diff_complete_algorithm.set_xticklabels(x_axis_values, \
                        rotation=(45))
            else:
                logging.error('Correct option for x-axis not provided to plot graphs')
                sys.exit(0)
            time_diff_complete_algorithm.set_ylabel('difference in execution time\nin microseconds')
            time_diff_complete_algorithm.set_title('Difference in execution time\nfor complete algorithm', \
                    loc='center', pad=10, fontsize=10, fontweight='bold')
            fig.legend(labels=['laplace', 'gaussian'], loc='lower center')
            if x_axis == 's':
                plt.savefig('plots/changing_sensor_count/single/exec_time_difference_graph_complete_algorithm.png', \
                        bbox_inches='tight')
            else:
                logging.error('Correct option for x-axis not provided to plot graphs')
                sys.exit(0)
            plt.show()
        elif plot_mode == 'multiple':
            fig = plt.figure(figsize=(14, 10))
            fig.subplots_adjust(bottom=0.2, wspace=0.6, hspace=0.7)
            time_diff_noise_add_before_split = fig.add_subplot(231)
            time_diff_noise_add_before_split.bar(x_axis_values, \
                    noise_add_before_split_gaussian_time_diff, \
                    width=-width, color='b', align='edge')
            time_diff_noise_add_before_split.bar(x_axis_values, \
                    noise_add_before_split_laplace_time_diff, \
                    width=width, color='r', align='edge')
            if x_axis == 's':
                time_diff_noise_add_before_split.set_xlabel('change in number of sensors')
                time_diff_noise_add_before_split.set_xticklabels(x_axis_values, \
                        rotation=(45))
            else:
                logging.error('Correct option for x-axis not provided to plot graphs')
                sys.exit(0)
            time_diff_noise_add_before_split.set_ylabel('difference in execution time\nin microseconds')
            time_diff_noise_add_before_split.set_title('Difference in execution time\nfor noise addition before splitting', \
                    loc='center', pad=10, fontsize=10, fontweight='bold')
            time_diff_for_split = fig.add_subplot(232)
            time_diff_for_split.bar(x_axis_values, for_split_time_diff, \
                    width=width, color='g', align='center')
            if x_axis == 's':
                time_diff_for_split.set_xlabel('change in number of sensors')
                time_diff_for_split.set_xticklabels(x_axis_values, rotation=(45))
            else:
                logging.error('Correct option for x-axis not provided to plot graphs')
                sys.exit(0)
            time_diff_for_split.set_ylabel('difference in execution time\nin microseconds')
            time_diff_for_split.set_title('Difference in execution time\nfor splitting', \
                    loc='center', pad=10, fontsize=10, fontweight='bold')
            time_diff_noise_add_after_split = fig.add_subplot(233)
            time_diff_noise_add_after_split.bar(x_axis_values, \
                    noise_add_after_split_time_diff, \
                    width=width, color='g', align='center')
            if x_axis == 's':
                time_diff_noise_add_after_split.set_xlabel('change in number of sensors')
                time_diff_noise_add_after_split.set_xticklabels(x_axis_values, \
                        rotation=(45))
            else:
                logging.error('Correct option for x-axis not provided to plot graphs')
                sys.exit(0)
            time_diff_noise_add_after_split.set_ylabel('difference in execution time\nin microseconds')
            time_diff_noise_add_after_split.set_title('Difference in execution time\nfor noise addition after splitting', \
                    loc='center', pad=10, fontsize=10, fontweight='bold')
            time_diff_for_partial_summations = fig.add_subplot(234)
            time_diff_for_partial_summations.bar(x_axis_values, \
                    for_partial_summations_time_diff, \
                    width=width, color='g', align='center')
            if x_axis == 's':
                time_diff_for_partial_summations.set_xlabel('change in number of sensors')
                time_diff_for_partial_summations.set_xticklabels(x_axis_values, rotation=(45))
            else:
                logging.error('Correct option for x-axis not provided to plot graphs')
                sys.exit(0)
            time_diff_for_partial_summations.set_ylabel('difference in execution time\nin microseconds')
            time_diff_for_partial_summations.set_title('Difference in execution time\nfor partial summations', \
                    loc='center', pad=10, fontsize=10, fontweight='bold')
            time_diff_complete_algorithm = fig.add_subplot(235)
            time_diff_complete_algorithm.bar(x_axis_values, \
                    complete_algorithm_laplace_time_diff, \
                    width=-width, color='b', align='edge')
            time_diff_complete_algorithm.bar(x_axis_values, \
                    complete_algorithm_gaussian_time_diff, \
                    width=width, color='r', align='edge')
            if x_axis == 's':
                time_diff_complete_algorithm.set_xlabel('change in number of sensors')
                time_diff_complete_algorithm.set_xticklabels(x_axis_values, \
                        rotation=(45))
            else:
                logging.error('Correct option for x-axis not provided to plot graphs')
                sys.exit(0)
            time_diff_complete_algorithm.set_ylabel('difference in execution time\nin microseconds')
            time_diff_complete_algorithm.set_title('Difference in execution time\nfor complete algorithm', \
                    loc='center', pad=10, fontsize=10, fontweight='bold')
            fig.legend(labels=['laplace', 'gaussian'], loc='lower center')
            if x_axis == 's':
                plt.savefig('plots/changing_sensor_count/multiple/exec_time_difference_graphs.png', \
                        bbox_inches='tight')
            else:
                logging.error('Correct option for x-axis not provided to plot graphs')
                sys.exit(0)
            plt.show()
        else:
            logging.error('Correct option for plot mode not provided to plot graphs')
            sys.exit(0)

def plot_distance_graphs(distance_values, x_axis_values, x_axis):
    '''
    graph 1 -> distance in centimeters vs number of sensors / epsilon
            -> distance - actual, central and split laplace noised and gaussian
               noised
    '''
    if len(x_axis_values) == (max_epsilon / epsilon_step) + 1:
        width = 0.05
    elif len(x_axis_values) == max_sensor_count / sensor_count_step:
        width = 0.75
    else:
        width = 0.4
    fig, distance = create_plot_single()
    distance.bar([value - (width * 1.5) for value in x_axis_values], \
            distance_values[0], width=-width, color='b', align='edge')
    distance.bar([value - (width * 0.5) for value in x_axis_values], \
            distance_values[1], width=-width, color='r', align='edge')
    distance.bar(x_axis_values, distance_values[2], \
            width=width, color='g', align='center')
    distance.bar([value + (width * 0.5) for value in x_axis_values], \
            distance_values[3], width=width, color='y', align='edge')
    distance.bar([value + (width * 1.5) for value in x_axis_values], \
            distance_values[4], width=width, color='k', align='edge')
    if x_axis == 'e':
        distance.set_xlabel('epsilon value')
    elif x_axis == 's':
        distance.set_xlabel('number of sensors')
    else:
        logging.error('Correct option for x-axis not provided to plot graphs')
        sys.exit(0)
    distance.set_ylabel('distance in centimeters')
    distance.set_title('Distance measured', fontweight='bold')
    fig.legend(labels=['actual', \
            'central method laplace', 'central method gaussian', \
            'split method laplace', 'split method gaussian'], \
            loc='lower center')
    if x_axis == 'e':
        plt.savefig('plots/changing_epsilon/distance_graphs.png', \
                bbox_inches='tight')
    elif x_axis == 's':
        plt.savefig('plots/changing_sensor_count/distance_graphs.png', \
                bbox_inches='tight')
    else:
        logging.error('Correct option for x-axis not provided to plot graphs')
        sys.exit(0)
    plt.show()

if __name__ == '__main__':
    args = setup_argument_parser()
    log_level = args.log_level
    if log_level != 'debug' and log_level != 'info':
        print('Correct log level not provided')
        sys.exit(0)
    setup_logging_config(log_level)
    ve = args.vary_epsilon
    vscnt = args.vary_sensor_count
    pu = args.plot_utility
    pe = args.plot_exectime
    pd = args.plot_distance
    pm = args.plot_mode
    from_file = args.from_file
    file_name_1 = 'distance_sensor_data_arduino_1.log'
    file_name_2 = 'distance_sensor_data_arduino_2.log'
    if from_file == 'yes':
        with open(file_name_1, 'r') as file_desc_1:
            data_partial_1 = file_desc_1.read()
        with open(file_name_2, 'r') as file_desc_2:
            data_partial_2 = file_desc_2.read()
        if data_partial_1 is None or data_partial_2 is None:
            logging.error('Read data is corrupt or mode is incorrect')
            sys.exit(0)
    elif from_file == 'no':
        ports = get_arduino_ports()
        if not ports:
            logging.error('Ports for Arduino not found')
            sys.exit(0)
        baudrate = 9600
        timeout = 10
        manager = Manager()
        return_dict = manager.dict()
        jobs = []
        if args is not None:
            if ve == 'yes' and vscnt == 'no':
                # data_partial_1 = get_data(ports[0], baudrate, timeout, 've')
                # data_partial_2 = get_data(ports[1], baudrate, timeout, 've')
                process_1 = Process(target=get_data, args=(1, return_dict, ports[0], baudrate, timeout, 've', file_name_1))
                process_2 = Process(target=get_data, args=(2, return_dict, ports[1], baudrate, timeout, 've', file_name_2))
            elif ve == 'no' and vscnt == 'yes':
                # data_partial_1 = get_data(ports[0], baudrate, timeout, 'vscnt')
                # data_partial_2 = get_data(ports[1], baudrate, timeout, 'vscnt')
                process_1 = Process(target=get_data, args=(1, return_dict, ports[0], baudrate, timeout, 'vscnt', file_name_1))
                process_2 = Process(target=get_data, args=(2, return_dict, ports[1], baudrate, timeout, 'vscnt', file_name_2))
            elif ve == 'no' and vscnt == 'no':
                # data_partial_1 = get_data(ports[0], baudrate, timeout, 'nochg')
                # data_partial_2 = get_data(ports[1], baudrate, timeout, 'nochg')
                process_1 = Process(target=get_data, args=(1, return_dict, ports[0], baudrate, timeout, 'nochg', file_name_1))
                process_2 = Process(target=get_data, args=(2, return_dict, ports[1], baudrate, timeout, 'nochg', file_name_2))
            else:
                logging.error('Correct combination of input parameters not provided')
                sys.exit(0)
        else:
            logging.error('Argument parser setup failed')
            sys.exit(0)
        jobs.append(process_1)
        jobs.append(process_2)
        process_1.start()
        process_2.start()
        for proc in jobs:
            proc.join()
        data_partial_1 = return_dict[1]
        data_partial_2 = return_dict[2]
    else:
        logging.error('Correct from file option not provided')
        sys.exit(0)
    data_partial_1 = data_partial_1.split('\n')
    data_partial_1.remove('')
    data_partial_2 = data_partial_2.split('\n')
    data_partial_2.remove('')
    logging.debug('data_partial_1 -> ' + str(data_partial_1))
    logging.debug('data_partial_2 -> ' + str(data_partial_2))
    sensitivity_summation = float(data_partial_1[0])
    distance_values = []
    if ve == 'yes':
        epsilon_values, distance_values_partial_1, exec_times_1 = create_lists(data_partial_1)
        epsilon_values, distance_values_partial_2, exec_times_2 = create_lists(data_partial_2)
        logging.debug('epsilon_values -> ' + str(epsilon_values))
        distance_values.append([value_1 + value_2 for value_1, value_2 in zip(distance_values_partial_1[0], distance_values_partial_2[0])])
        distance_values.append([(value + laplace(sensitivity_summation / 0.1)) if math.isclose(epsilon_values[iterator], 0.0) else (value + laplace(sensitivity_summation / epsilon_values[iterator])) for iterator, value in enumerate(distance_values[0])])
        distance_values.append([(value + gaussian(0.0, sensitivity_summation / 0.1)) if math.isclose(epsilon_values[iterator], 0.0) else (value + gaussian(0.0, sensitivity_summation / epsilon_values[iterator])) for iterator, value in enumerate(distance_values[0])])
    elif vscnt == 'yes':
        sensor_count_values_partial_1, distance_values_partial_1, exec_times_1 = create_lists(data_partial_1)
        sensor_count_values_partial_2, distance_values_partial_2, exec_times_2 = create_lists(data_partial_2)
        sensor_count_values = [int(value_1 + value_2) for value_1, value_2 in zip(sensor_count_values_partial_1, sensor_count_values_partial_2)]
        logging.debug('sensor_count_values -> ' + str(sensor_count_values))
        distance_values.append([value_1 + value_2 for value_1, value_2 in zip(distance_values_partial_1[0], distance_values_partial_2[0])])
        epsilon = float(data_partial_1[1])
        distance_values.append([value + laplace(sensitivity_summation / epsilon) for value in distance_values[0]])
        distance_values.append([value + gaussian(0.0, sensitivity_summation / epsilon) for value in distance_values[0]])
    else:
        logging.info('Neither epsilon nor sensor count varied')
        sys.exit(0)
    distance_values.append([value_1 + value_2 for value_1, value_2 in zip(distance_values_partial_1[1], distance_values_partial_2[1])])
    distance_values.append([value_1 + value_2 for value_1, value_2 in zip(distance_values_partial_1[2], distance_values_partial_2[2])])
    exec_times = [[(value_1 + value_2) / 2 for value_1, value_2 in zip(list_1, list_2)] for list_1, list_2 in zip(exec_times_1, exec_times_2)]
    logging.debug('distance_values -> ' + str(distance_values))
    logging.debug('exec_times -> ' + str(exec_times))
    mape_utility_laplace, mape_utility_gaussian, \
            smape_utility_laplace, smape_utility_gaussian, \
            mmape_utility_laplace, mmape_utility_gaussian = \
            create_utility_lists(distance_values)
    if None in mape_utility_laplace[0] or None in mape_utility_laplace[1] or \
            None in mape_utility_gaussian[0] or \
            None in mape_utility_gaussian[1]:
                mape_utility_laplace = None
                mape_utility_gaussian = None
    if ve == 'yes':
        if pu == 'yes':
            plot_utility_graphs(mape_utility_laplace, mape_utility_gaussian, \
                    smape_utility_laplace, smape_utility_gaussian, \
                    mmape_utility_laplace, mmape_utility_gaussian, \
                    epsilon_values, 'e', pm)
        if pe == 'yes':
            plot_exec_time_graphs(exec_times, epsilon_values, 'e', pm)
        if pd == 'yes':
            plot_distance_graphs(distance_values, epsilon_values, 'e')
    elif vscnt == 'yes':
        if pu == 'yes':
            plot_utility_graphs(mape_utility_laplace, mape_utility_gaussian, \
                    smape_utility_laplace, smape_utility_gaussian, \
                    mmape_utility_laplace, mmape_utility_gaussian, \
                    sensor_count_values, 's', pm)
        if pe == 'yes':
            plot_exec_time_graphs(exec_times, sensor_count_values, 's', pm)
        if pd == 'yes':
            plot_distance_graphs(distance_values, sensor_count_values, 's')
    else:
        loggin.info('Neither epsilon nor sensor count varied')
        sys.exit(0)
    logging.debug('mape_utility_laplace -> ' + str(mape_utility_laplace))
    logging.debug('mape_utility_gaussian -> ' + str(mape_utility_gaussian))
    logging.debug('smape_utility_laplace -> ' + str(smape_utility_laplace))
    logging.debug('smape_utility_gaussian -> ' + str(smape_utility_gaussian))
    logging.debug('mmape_utility_laplace -> ' + str(mmape_utility_laplace))
    logging.debug('mmape_utility_gaussian -> ' + str(mmape_utility_gaussian))