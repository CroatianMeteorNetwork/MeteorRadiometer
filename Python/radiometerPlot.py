
# Plots all radiometer format CSV files into plots
# Modify the csv_directory varibale to tell the script where are the raw radiometer CSV files



import os
import errno
import matplotlib.pyplot as plt
import numpy as np
import datetime
import matplotlib.dates as mdates

def mkdir_p(path):
    """ Make dir if it doesn't exist. """
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

@np.vectorize
def datestr2datetime(date_str):
    """ Converts date string to datetime object. """

    return datetime.datetime.strptime(date_str, "%Y-%m-%d_%H.%M.%S.%f")


def loadData(file_name):
    """ Load data from a file. """

    # Load data from file
    #data = np.loadtxt(file_name, delimiter = ',', dtype = {'names': ('time', 'value'), 'formats': ('|S19', 'S5')})
    data = np.loadtxt(file_name, delimiter = ',', dtype='string')

    # Split array
    data = np.reshape(data, (-1, 2))
    time_data, value_data = np.hsplit(data, 2)

    # Convert time string to datetime object
    # time_data = datestr2datetime(time_data)

    return time_data, value_data



if __name__ == '__main__':


    # Where are the CSV files relative to the script
    csv_directory = '2017071718'

    # Directory where to output the plots
    plot_dir = 'plots'

    #Make plot dir
    mkdir_p(csv_directory + os.sep + plot_dir)

    for file_name in os.listdir(csv_directory):

        if '.csv' in file_name:

            # Read beginning time from file name
            #2017-07-18_00.07.19.324000
            beg_time = datestr2datetime(file_name.replace('.csv', ''))

            # Load data
            time_data, value_data = loadData(csv_directory + os.sep + file_name)

            datetime_data = []

            for t in time_data:
                
                # Calculate datetime of every data point
                t = beg_time + datetime.timedelta(seconds=float(t[0]))

                datetime_data.append(t)

            # Plot data
            plt.plot(datetime_data, value_data)

            plot_name = '.'.join(file_name.split('.')[:-2])

            print plot_name

            # Add labels
            plt.title('Lightcurve ' + plot_name + ' UTC')
            plt.xlabel('Time (s)')
            plt.ylabel('ADU')

            # Set Y limits
            plt.ylim((0, 2**16))

            # Modify tick number and enable grid
            myFmt = mdates.DateFormatter('%S')
            ax = plt.gca()
            ax.xaxis.set_major_formatter(myFmt)
            ax.grid(True)

            # Save plot
            plt.savefig(csv_directory + os.sep + plot_dir + os.sep + file_name + '.png')

            # Clear plot
            plt.clf()
