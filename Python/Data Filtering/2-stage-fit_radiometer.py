""" This script is used for filtering meteor radiometer data by modelling the noise and substracting it
    from the input signal.
"""


# The MIT License

# Copyright (c) 2016 Denis Vida

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
import datetime
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# Input and output file names
input_file_name = '2016-03-16_03.17.18.178.csv'
parameters_output_file = 'parameters.txt'

# Samples per second of the ADC
sps = 500

# Base frequency of the noise
base_freq = 2*np.pi*50

# Sample range (seconds)
sample_range_beg = 0.8
sample_range_end = 2.0

# Full fit range
full_range_beg = 0.0
full_range_end = 10.0

# Filtered custom plot range
filtered_range_beg = 0.2
filtered_range_end = 0.8


def func(x, a, b, c, d, e, f, g, h, i, j, k, l, m):
    """ A function that defines the noise model. """

    # 5 harmonics sine with linearly variable frequency (frequency drift is "m")
    c = c + m*x
    return a + b*np.sin(c*x+d)+e*np.sin(2*c*x+f)+g*np.sin(3*c*x+h)+i*np.sin(4*c*x+j)+k*np.sin(5*c*x+l)


def plotResult(x_data, y_data, func, popt, highlight=False, highlight_min=0, highlight_max=0):
    """ Plots fitted data. """

    # Plot original

    plt.subplot(3, 1, 1)

    if highlight:
        # Highlight the sample area
        plt.axvspan(highlight_min, highlight_max, facecolor='r', alpha=0.5, lw=0)

    plt.plot(x_data, y_data)

    plt.title('Original')
    plt.ylabel('ADU')

    # Plot model
    plt.subplot(3, 1, 2)
    plt.plot(x_data, func(x_data, *popt))

    plt.title('Model')
    plt.ylabel('ADU')


    # Plot filtered
    plt.subplot(3, 1, 3)
    plt.plot(x_data, y_data - func(x_data, *popt))

    plt.title('Filtered')
    plt.xlabel('Time (s)')
    plt.ylabel('ADU')

    plt.show()
    plt.clf()


def printParameters(popt):
    """ Print fitted parameter values. """

    a = 97
    for i, param in enumerate(popt):
        print chr(a+i), '=', param

def saveParameters(popt, filename):
    """ Saves fit parameters to a file. """

    with open(filename, 'w') as f:

        a = 97
        for i, param in enumerate(popt):
            f.write(chr(a+i)+' = '+str(param)+'\n')


def loadCSV(file_name):
    """ Load the radiometer format CSV file. """

    # Load file data
    x_data = []
    y_data = []

    with open(input_file_name) as f:
        for line in f.readlines():
            line = line.split(',')
            x_data.append(line[0])
            y_data.append(line[1])

    # Convert x_data from string date format to seconds from the beginning of the file
    time_list = []
    for entry in x_data:
        time_list.append(datetime.datetime.strptime(entry, '%Y%m%d-%H%M%S.%f'))

    # Normalize so that the first point is 0 seconds and convert all data to seconds from the beginning
    first_date = time_list[0]
    for i, entry in enumerate(time_list):
        time_list[i] = entry - first_date
        time_list[i] = time_list[i].seconds + time_list[i].microseconds/1000000.0


    # Convert data to numpy arrays
    x_data = np.array(time_list, dtype=np.float64)
    y_data = np.array(y_data, dtype=np.float64)

    return x_data, y_data


def saveCSV(file_name, x_data, y_data):
    """ Save a CSV file with filtered data. """

    with open(file_name, 'w') as f:
        for i in range(len(x_data)):
            f.write('{:.6f}'.format(x_data[i]) + ',' + '{:06.6f}'.format(y_data[i]) + '\n')

    

# Load the CSV file
x_data, y_data = loadCSV(input_file_name)

### INITIAL FIT ON THE SELECTED PART OF THE DATA ###

# Initial guess
p0 = [np.mean(y_data), 1, base_freq, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0]

# Fit on part of the data data (initial guess refinement)
popt, pcov = curve_fit(func, x_data[int(sample_range_beg*sps) : int(sample_range_end*sps)], 
    y_data[int(sample_range_beg*sps) : int(sample_range_end*sps)], p0, maxfev = 10000)

print 'Sample parameters: '
printParameters(popt)

# Show sample fit
plotResult(x_data, y_data, func, popt, highlight=True, highlight_min=sample_range_beg, 
    highlight_max=sample_range_end)



### FIT ON ALL DATA POINTS ###

# Fit all data with approximated parameters
popt, pcov = curve_fit(func, x_data[int(full_range_beg*sps) : int(full_range_end*sps)], 
    y_data[int(full_range_beg*sps) : int(full_range_end*sps)], popt, maxfev = 10000)

print 'Final parameters: '
printParameters(popt)

# Save parameters to a file
saveParameters(popt, parameters_output_file)

# Save filtered data to a file
saveCSV("".join(input_file_name.split('.')[:-2]) + '_filtered.csv', x_data, y_data - func(x_data, *popt))

# Show full fit
plotResult(x_data, y_data, func, popt, highlight=True, highlight_min=full_range_beg, 
    highlight_max=full_range_end)


# Plot selected range of the filtered data
plt.plot(x_data, y_data - func(x_data, *popt))

plt.title('Filtered data')
plt.xlabel('Time (s)')
plt.ylabel('ADU')

plt.xlim((filtered_range_beg, filtered_range_end))

plt.show()