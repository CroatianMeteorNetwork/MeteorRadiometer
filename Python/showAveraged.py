""" Averages every N points in the radiometer file and shows them on a line graph. """

import matplotlib.pyplot as plt
import numpy as np

# File name of the input file
file_name = '2016-08-06_20.49.40.465000.csv'

# Decimation level (average every N measurements)
every_N = 10

# Load the radiometer data into an numpy array
radiometer_data = np.loadtxt(open(file_name), delimiter=',')

# Take only the intensity data
intensity_data = radiometer_data[:,1]

# Cut the array lenght to a multiple of the decimation level
intensity_data = intensity_data[:-(len(intensity_data) % every_N)]

# Perform averaging
averaged_data = np.mean(intensity_data.reshape(-1, every_N), axis=1)

# Plot the averaged results
plt.plot(np.arange(0,len(averaged_data)), averaged_data)

# Plot the mean line and stddev lines
averaged_mean = np.mean(averaged_data)
averaged_std = np.std(averaged_data)

# Plot the mean line
plt.plot((0, len(averaged_data)), (averaged_mean, averaged_mean), 'g')

# Plot one standard deviation lines
plt.plot((0, len(averaged_data)), (averaged_mean-2*averaged_std, averaged_mean-2*averaged_std), 'r', ls='--')
plt.plot((0, len(averaged_data)), (averaged_mean+2*averaged_std, averaged_mean+2*averaged_std), 'r', ls='--')

# Set the vertical limit to the plot
plt.ylim([0, 65536])
plt.show()