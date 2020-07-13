from multiprocessing import Process, Manager

def get_data(process_num, return_dict, baudrate, port, timeout, mode):
    data = str(process_num) + ' ' + str(baudrate) + ' ' + port + ' ' + str(timeout) + ' ' + str(mode)
    print(data)
    for i in range(0, 500):
        print(str(process_num) + ' ' + str(i))
    return_dict[process_num] = data

if __name__ == '__main__':
    manager = Manager()
    return_dict = manager.dict()
    jobs = []
    process_1 = Process(target=get_data, args=(0, return_dict, 9600, '/dev/ttyACM0', 10, 'nochg'))
    process_2 = Process(target=get_data, args=(1, return_dict, 9600, '/dev/ttyACM1', 10, 'nochg'))
    jobs.append(process_1)
    jobs.append(process_2)
    process_1.start()
    process_2.start()

    for proc in jobs:
        proc.join()
    print(return_dict[0], return_dict[1])