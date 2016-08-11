import os
import csv
import numpy as np
import time
import datetime
from subprocess import call
import shutil


def analyze(folder_name):
    """ Creates the statistics of the files in the night folder. """
    
    start = time.time()

    average_array = np.array([])
    stan_dev_array = np.array([])
    minimum_array = np.array([])
    maximum_array = np.array([])
    f_average_array = np.array([])
    f_stan_dev_array = np.array([])
    f_minimum_array = np.array([])
    f_maximum_array = np.array([])
    file_name_array = np.array([])

    result_file = 'results_'+folder_name.replace(os.sep, '_')+'.csv'

    print 'Listing all files..'
    for file_name in sorted(os.listdir(folder_name)):
        data = []
        if file_name.endswith(".csv"):
            print file_name
            f = open(os.path.join(folder_name, file_name), 'rt')
            try:
                reader = csv.reader(f)
                for row in reader:
                    data.append(row)
            finally:
                f.close()

            values = []
            if data:
                for i in data:
                    values.append(float(i[1]))

                averages = []
                for i in range(0, len(values) - 10):
                    temp = [int(values[i]), int(values[i + 1]), int(values[i + 2]), int(values[i + 3]), int(values[i + 4]),
                            int(values[i + 5]), int(values[i + 6]), int(values[i + 7]), int(values[i + 8]), int(values[i + 9])]
                    avg = reduce(lambda x, y: x + y, temp) / len(temp)
                    averages.append(avg)

                file_name_array = np.append(file_name_array, ['.'.join(file_name.split('.')[:-1])])
                
                average_array = np.append(average_array, [np.mean(values)])
                stan_dev_array = np.append(stan_dev_array, [np.std(values)])
                minimum_array = np.append(minimum_array, [np.min(values)])
                maximum_array = np.append(maximum_array, [np.max(values)])
                f_average_array = np.append(f_average_array, [np.mean(averages)])
                f_stan_dev_array = np.append(f_stan_dev_array, [np.std(averages)])
                f_minimum_array = np.append(f_minimum_array, [np.min(averages)])
                f_maximum_array = np.append(f_maximum_array, [np.max(averages)])

    output = np.column_stack((file_name_array.flatten(), average_array.flatten(), stan_dev_array.flatten(), minimum_array.flatten(), maximum_array.flatten(),
                                 f_average_array.flatten(), f_stan_dev_array.flatten(), f_minimum_array.flatten(), f_maximum_array.flatten()))

    np.savetxt(result_file.replace(':', '.'), output, fmt=['%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s'], delimiter=';',
               header='Time;Mean;Stddev;Min;Max;Averaged mean;Stddev;Min;Max')

    print time.time() - start


if __name__ == '__main__':

    folder_name = '2016080809'

    analyze(folder_name)
        
