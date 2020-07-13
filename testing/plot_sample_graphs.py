import matplotlib.pyplot as plt
import math

'''
sensor_values = [5, 10, 15, 20, 25, 30, 35, 40, 45]
epsilon_values = [0.0, 0.5, 1.0, 1.5, 2.0]
mape_utility_laplace = [[0.0, 1.5277111525932508e-05, 1.833331805559793e-05, 1.7304348888253885e-05, 1.4249798975990911e-05], [0.0, 0.0006956178114824733, 0.0008423141128862466, 0.0, 0.0]]
mape_utility_gaussian = [[0.0, 1.8332533831193114e-05, 2.4444424074068815e-05, 1.9340154639671576e-05, 1.1196270623913511e-05], [0.0, 0.0, 0.0, 0.0, 0.0]]
smape_utility_laplace = [[0.0, 1.5277111525932508e-05, 1.833331805559793e-05, 1.7304348888253885e-05, 1.4249798975990911e-05], [0.0, 0.0006956178114824733, 0.0008423141128862466, 0.0, 0.0]]
smape_utility_gaussian = [[0.0, 1.8332533831193114e-05, 2.4444424074068815e-05, 1.9340154639671576e-05, 1.1196270623913511e-05], [0.0, 0.0, 0.0, 0.0, 0.0]]
mmape_utility_laplace = [[0.0, 1.5277111525932508e-05, 1.833331805559793e-05, 1.7304348888253885e-05, 1.4249798975990911e-05], [0.0, 0.0006956178114824733, 0.0008423141128862466, 0.0, 0.0]]
mmape_utility_gaussian = [[0.0, 1.8332533831193114e-05, 2.4444424074068815e-05, 1.9340154639671576e-05, 1.1196270623913511e-05], [0.0, 0.0, 0.0, 0.0, 0.0]]
exec_times = [[336.0, 768.0, 808.0, 812.0, 792.0], [352.0, 788.0, 800.0, 820.0, 848.0], [13220.0, 13156.0, 13200.0, 13212.0, 13228.0], [18724.0, 18592.0, 18768.0, 18700.0, 18772.0], [560.0, 760.0, 540.0, 540.0, 548.0], [32124.0, 31692.0, 31672.0, 31888.0, 32244.0], [32640.0, 32196.0, 32188.0, 32228.0, 32100.0]]
distance_values = [[9827.38, 9818.61, 9818.19, 9824.12, 9824.7], [9827.38, 9818.76, 9818.37, 9824.29, 9824.84], [9827.38, 9818.79, 9818.43, 9824.31, 9824.81], [9827.38, 9825.44, 9826.46, 9824.12, 9824.7], [9827.38, 9818.61, 9818.19, 9824.12, 9824.7]]
'''
epsilon_values = [5, 10, 15, 20, 25, 30, 35, 40, 45]
sensor_values = [0.0, 0.5, 1.0, 1.5, 2.0]
mape_utility_laplace = [[7.074637424825544e-05, 2.828914333399126e-05, 2.3567785665215787e-05, 1.4165309157859487e-05, 1.413443544243098e-05, 1.1779090230015573e-05, 8.078637456999155e-06, 7.059691456178487e-06, 6.288210705358597e-06], [0.0003254333215422967, 0.00031825286250772327, 0.00032052188504569145, 0.00031871945605199946, 0.0, 0.00032039125426100873, 0.0, 0.0003176861155283529, 0.000319126693297342]]
mape_utility_gaussian = [[5.6597099398604345e-05, 2.828914333399126e-05, 1.885422853208689e-05, 1.4165309157859487e-05, 1.1307548353893365e-05, 9.423272184141014e-06, 8.078637456999155e-06, 7.059691456178487e-06, 6.288210705358597e-06], [0.0002829854969933434, 0.0002758191475065756, 0.0002828134279815177, 0.0, 0.0002798618217590536, 0.0, 0.0, 0.0, 0.000279825376388815]]
smape_utility_laplace = [[7.074637424825544e-05, 2.828914333399126e-05, 2.3567785665215787e-05, 1.4165309157859487e-05, 1.413443544243098e-05, 1.1779090230015573e-05, 8.078637456999155e-06, 7.059691456178487e-06, 6.288210705358597e-06], [0.0003254333215422967, 0.00031825286250772327, 0.00032052188504569145, 0.00031871945605199946, 0.0, 0.00032039125426100873, 0.0, 0.0003176861155283529, 0.000319126693297342]]
smape_utility_gaussian = [[5.6597099398604345e-05, 2.828914333399126e-05, 1.885422853208689e-05, 1.4165309157859487e-05, 1.1307548353893365e-05, 9.423272184141014e-06, 8.078637456999155e-06, 7.059691456178487e-06, 6.288210705358597e-06], [0.0002829854969933434, 0.0002758191475065756, 0.0002828134279815177, 0.0, 0.0002798618217590536, 0.0, 0.0, 0.0, 0.000279825376388815]]
mmape_utility_laplace = [[7.074637424825544e-05, 2.828914333399126e-05, 2.3567785665215787e-05, 1.4165309157859487e-05, 1.413443544243098e-05, 1.1779090230015573e-05, 8.078637456999155e-06, 7.059691456178487e-06, 6.288210705358597e-06], [0.0003254333215422967, 0.00031825286250772327, 0.00032052188504569145, 0.00031871945605199946, 0.0, 0.00032039125426100873, 0.0, 0.0003176861155283529, 0.000319126693297342]]
mmape_utility_gaussian = [[5.6597099398604345e-05, 2.828914333399126e-05, 1.885422853208689e-05, 1.4165309157859487e-05, 1.1307548353893365e-05, 9.423272184141014e-06, 8.078637456999155e-06, 7.059691456178487e-06, 6.288210705358597e-06], [0.0002829854969933434, 0.0002758191475065756, 0.0002828134279815177, 0.0, 0.0002798618217590536, 0.0, 0.0, 0.0, 0.000279825376388815]]
exec_times = [[56.0, 108.0, 160.0, 212.0, 264.0, 316.0, 376.0, 420.0, 484.0], [56.0, 104.0, 156.0, 204.0, 252.0, 304.0, 352.0, 404.0, 460.0], [1492.0, 2980.0, 4440.0, 5900.0, 7380.0, 8828.0, 10256.0, 11824.0, 13324.0], [2112.0, 4184.0, 6284.0, 8216.0, 10464.0, 12400.0, 14136.0, 16652.0, 18868.0], [88.0, 180.0, 268.0, 288.0, 464.0, 488.0, 480.0, 544.0, 848.0], [3788.0, 7540.0, 11312.0, 15032.0, 18564.0, 22504.0, 25908.0, 29916.0, 31844.0], [3780.0, 7480.0, 11180.0, 14644.0, 18592.0, 22052.0, 25276.0, 29460.0, 32004.0]]
distance_values = [[706.75, 1413.97, 2121.54, 2823.8, 3537.46, 4244.81, 4951.33, 5665.97, 6361.11], [706.8, 1414.01, 2121.59, 2823.84, 3537.51, 4244.86, 4951.37, 5666.01, 6361.15], [706.79, 1414.01, 2121.58, 2823.84, 3537.5, 4244.85, 4951.37, 5666.01, 6361.15], [706.98, 1414.42, 2122.22, 2824.7, 3537.46, 4246.17, 4951.33, 5667.77, 6363.14], [706.95, 1414.36, 2122.14, 2823.8, 3538.45, 4244.81, 4951.33, 5665.97, 6362.89]]

fig = plt.figure(figsize=(14, 10))
fig.subplots_adjust(bottom=0.2, wspace=0.6, hspace=0.6)
mape = fig.add_subplot(221)
mape.plot(epsilon_values, mape_utility_laplace[0], 'bo-', label='central method using laplace')
mape.plot(epsilon_values, mape_utility_gaussian[0], 'rs-', label='central method using gaussian')
mape.plot(epsilon_values, mape_utility_laplace[1], 'g^-', label='split method using laplace')
mape.plot(epsilon_values, mape_utility_gaussian[1], 'yx-', label='split method using gaussian')
# mape.legend(loc='best')
mape.set_xlabel('epsilon value')
mape.set_ylabel('utility in MAPE')
mape.set_title('MAPE utility', loc='center')
smape = fig.add_subplot(222)
smape.plot(epsilon_values, smape_utility_laplace[0], 'bo-', label='central method using laplace')
smape.plot(epsilon_values, smape_utility_gaussian[0], 'rs-', label='central method using gaussian')
smape.plot(epsilon_values, smape_utility_laplace[1], 'g^-', label='split method using laplace')
smape.plot(epsilon_values, smape_utility_gaussian[1], 'yx-', label='split method using gaussian')
smape.set_xlabel('epsilon value')
smape.set_ylabel('utility in SMAPE')
smape.set_title('SMAPE utility', loc='center')
mmape = fig.add_subplot(223)
mmape.plot(epsilon_values, mmape_utility_laplace[0], 'bo-', label='central method using laplace')
mmape.plot(epsilon_values, mmape_utility_gaussian[0], 'rs-', label='central method using gaussian')
mmape.plot(epsilon_values, mmape_utility_laplace[1], 'g^-', label='split method using laplace')
mmape.plot(epsilon_values, mmape_utility_gaussian[1], 'yx-', label='split method using gaussian')
mmape.set_xlabel('epsilon value')
mmape.set_ylabel('utility in MMAPE')
mmape.set_title('MMAPE utility', loc='center')
log_mmape = fig.add_subplot(224)
log_mmape.plot(epsilon_values, [math.log(value) if value != 0.0 else 0.0 for value in mmape_utility_laplace[0]], 'bo-', label='central method using laplace')
log_mmape.plot(epsilon_values, [math.log(value) if value != 0.0 else 0.0 for value in mmape_utility_gaussian[0]], 'rs-', label='central method using gaussian')
log_mmape.plot(epsilon_values, [math.log(value) if value != 0.0 else 0.0 for value in mmape_utility_laplace[1]], 'g^-', label='split method using laplace')
log_mmape.plot(epsilon_values, [math.log(value) if value != 0.0 else 0.0 for value in mmape_utility_gaussian[1]], 'yx-', label='split method using gaussian')
log_mmape.set_xlabel('epsilon value')
log_mmape.set_ylabel('utility in log(MMAPE)')
log_mmape.set_title('MMAPE utility', loc='center')
handles, labels = mape.get_legend_handles_labels()
fig.legend(handles, labels, loc='lower center')
plt.show()

epsilon_values = ['0-5', '5-10', '10-15', '15-20', '20-25', '25-30', '30-35', '35-40', '40-45']
if len(epsilon_values) == 5:
    width = 0.1
elif len(epsilon_values) == 9:
    width = 0.3
else:
    width = 0.75
fig = plt.figure(figsize=(14, 10))
fig.subplots_adjust(bottom=0.2, wspace=0.6, hspace=0.6)
exec_time_noise_add_before_split = fig.add_subplot(231)
exec_time_noise_add_before_split.bar(epsilon_values[1:], exec_times[0][1:], width=-width, color='b', align='edge')
exec_time_noise_add_before_split.bar(epsilon_values[1:], exec_times[1][1:], width=width, color='r', align='edge')
exec_time_noise_add_before_split.set_xlabel('epsilon value')
exec_time_noise_add_before_split.set_xticklabels(epsilon_values[1:], rotation=(45))
exec_time_noise_add_before_split.set_ylabel('execution time\nin microseconds')
exec_time_noise_add_before_split.set_title('Execution time for noise addition before splitting', loc='center', pad=10, fontsize=10, fontweight='bold')
exec_time_for_split = fig.add_subplot(232)
exec_time_for_split.bar(epsilon_values[1:], exec_times[2][1:], width=width, color='g', align='center')
exec_time_for_split.set_xlabel('epsilon value')
exec_time_for_split.set_xticklabels(epsilon_values[1:], rotation=(45))
exec_time_for_split.set_ylabel('execution time\nin microseconds')
exec_time_for_split.set_title('Execution time for splitting', loc='center', pad=10, fontsize=10, fontweight='bold')
exec_time_noise_add_after_split = fig.add_subplot(233)
exec_time_noise_add_after_split.bar(epsilon_values[1:], exec_times[3][1:], width=width, color='g', align='center')
exec_time_noise_add_after_split.set_xlabel('epsilon value')
exec_time_noise_add_after_split.set_xticklabels(epsilon_values[1:], rotation=(45))
exec_time_noise_add_after_split.set_ylabel('execution time\nin microseconds')
exec_time_noise_add_after_split.set_title('Execution time for noise addition after splitting', loc='center', pad=10, fontsize=10, fontweight='bold')
exec_time_for_summation = fig.add_subplot(234)
exec_time_for_summation.bar(epsilon_values[1:], exec_times[4][1:], width=width, color='g', align='center')
exec_time_for_summation.set_xlabel('epsilon value')
exec_time_for_summation.set_xticklabels(epsilon_values[1:], rotation=(45))
exec_time_for_summation.set_ylabel('execution time\nin microseconds')
exec_time_for_summation.set_title('Execution time for summation', loc='center', pad=10, fontsize=10, fontweight='bold')
exec_time_complete_algorithm = fig.add_subplot(235)
exec_time_complete_algorithm.bar(epsilon_values[1:], exec_times[5][1:], width=-width, color='b', align='edge')
exec_time_complete_algorithm.bar(epsilon_values[1:], exec_times[6][1:], width=width, color='r', align='edge')
exec_time_complete_algorithm.set_xlabel('epsilon value')
exec_time_complete_algorithm.set_ylabel('execution time\nin microseconds')
exec_time_complete_algorithm.set_xticklabels(epsilon_values[1:], rotation=(45))
exec_time_complete_algorithm.set_title('Execution time for complete algorithm', loc='center', pad=10, fontsize=10, fontweight='bold')
fig.legend(labels=['laplace', 'gaussian'], loc='lower center')
plt.show()

epsilon_values = [5, 10, 15, 20, 25, 30, 35, 40, 45]
if len(epsilon_values) == 5:
    width = 0.05
elif len(epsilon_values) == 9:
    width = 0.75
else:
    width = 0.4
fig = plt.figure(figsize=(14, 10))
fig.subplots_adjust(bottom=0.25)
distance = fig.add_subplot(111)
distance.bar([value - (width * 1.5) for value in epsilon_values], distance_values[0], width=-width, color='b', align='edge')
distance.bar([value - (width * 0.5) for value in epsilon_values], distance_values[1], width=-width, color='r', align='edge')
distance.bar(epsilon_values, distance_values[2], width=width, color='g', align='center')
distance.bar([value + (width * 0.5) for value in epsilon_values], distance_values[3], width=width, color='y', align='edge')
distance.bar([value + (width * 1.5) for value in epsilon_values], distance_values[4], width=width, color='k', align='edge')
distance.set_xlabel('epsilon value')
distance.set_ylabel('distance in centimeters')
distance.set_title('Distance measured')
fig.legend(labels=['actual', 'central method laplace', 'central method gaussian', 'split method laplace', 'split method gaussian'], loc='lower center')
# plt.show()