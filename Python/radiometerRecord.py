
# Record data from the radiometer into CSV files
# Modify the port = 'COM4' variable to your COM port
# Define recording length by changing the record_duration variable value

import serial
import time
import datetime
import matplotlib.pyplot as plt
import numpy as np

def waitResponse(ser, char):
    """ Wait for response from Arduino while toggling iris. """
    while 1:
        print 'Waiting...'
        time.sleep(0.2)
        ser.write(char)
        if "Response" in ser.readline():
            break

def recordData(ser):
    """ Run radiometer data recording for one data block. """
    data_array = np.array([], dtype=np.uint16)
    #times_array = np.array([], dtype=np.float32)
    times_array = np.array([])

    first_read = True 

    # Flush input buffer
    ser.flushInput()

    while 1:
        
        if not first_read:
            if (time.clock() - record_start >= data_block_time):
                break
                    
        try:
            b1 = ord(ser.read(1))
            b2 = ord(ser.read(1))
        except:
            continue

        # Calculate ADC value from 2 bytes transfered via COM interface
        serial_value = b1 + b2*256
        if serial_value != '':
            if first_read:
                first_read = False
                record_start = time.clock()
                time_start = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S.%f")[0:-3]
                print 'start', time_start

            #print serial_value

            # Add value to data list
            try:

                # Numpy arrays
                #data_array = np.append(data_array, [4096-serial_value])
                data_array = np.append(data_array, [serial_value])
                times_array = np.append(times_array, [datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S.%f")[0:-3]])


            except:
                print 'Error!'
                print serial_value
                break

    run_duration = time.clock() - record_start

    # Samples per second
    sps = len(data_array) / run_duration
    print 'Calculated SPS: ', sps

    return time_start, times_array, data_array


def initConnection(port = 'COM4'):
    """ Initialize connection to Arduino. """
    # Initalize serial connection, block read until new data is recieved
    ser = serial.Serial(port, 115200)

    # Wait for initialization
    time.sleep(2)

    # Open iris
    waitResponse(ser, "1")

    # Wait for the iris to open
    time.sleep(2)

    print 'Connected!'

    # Flush input buffer
    ser.flushInput()

    return ser

def closeConnection(ser):
    """ Close connection to Arduino. """
    print 'Ending data capture'

    # Close iris
    waitResponse(ser, '0')

    # Close serial communication
    ser.close()

def writeData(file_name, times_array, data_array):
    """ Write data to a file. """

    output = np.column_stack((times_array.flatten(), data_array.flatten()))
    #np.savetxt(file_name.replace(':', '.'), output, fmt = ['%2.5f', '%d'], delimiter = ',')
    np.savetxt(file_name.replace(':', '.'), output, fmt = ['%s', '%s'], delimiter = ',')


if __name__ == '__main__':

    # Record duration in hours
    #record_duration = 30.0/60/60.0 #hrs
    record_duration = 8 #hrs

    # Duration of a single time clock in seconds
    data_block_time = 10.24 #s

    print 'Recording duration: ', record_duration, 'hrs'
    print 'Data block duration: ', data_block_time, 's'

    # Initialize connection
    ser = initConnection()

    for i in range(int(record_duration*60*60/data_block_time)):
        # Run data recording
        time_start, times_array, data_array = recordData(ser)

        # Write data to a file
        writeData(str(time_start) + '.csv', times_array, data_array)

    # Close connection
    closeConnection(ser)