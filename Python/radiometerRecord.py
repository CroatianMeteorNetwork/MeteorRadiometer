# The MIT License (MIT)

# Copyright (c) 2016 Croatian Meteor Network

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import ephem
import datetime
import time
import serial
import numpy as np
import threading, Queue
import logging
import os
import sys
import errno
import shutil
from subprocess import call



def mkdirp(path):
    """ Makes a directory and handles all errors.
    """

    try:
        os.makedirs(path)
    except OSError, exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            print 'An error occured:'
            raise



def wordDayDuration(lat, lon, elevation):
    """Function that calculates start time and duration of capturing
    Reqiured inputs: Latitude, longitude, elevation
    Outputs: When to start recording (start_time) and for how long (duration), returned as list.
       start_time returns 'True' if it needs to start immediately
       duration returns a number of hours rounded %.2f"""

    o=ephem.Observer()
    o.lat=str(lat)
    o.long=str(lon)
    o.elevation=elevation
    o.horizon = '-5:26' #Correction for 30-minute later start/ending
    s=ephem.Sun()
    s.compute()

    next_rise=ephem.localtime(o.next_rising(s))
    next_set=ephem.localtime(o.next_setting(s))

    current_time=datetime.datetime.now()

    #Should we start recording now?
    if next_set>next_rise: 
        start_time=True
    else:
        start_time=next_set

    #For how long should we record?
    if start_time==True: 
        duration=next_rise-current_time
    else:
        duration=next_rise-next_set

    # Recalculate the recording time to hours and round to 4 decimals
    duration=round(duration.total_seconds()/60/60, 4)

    return (start_time, duration)



def currentMicroTime():
    """ Returns the number of milliseconds since epoch. """

    return int(round(time.time() * 1000000))



def waitResponse(ser, char):
    """ Wait for response from Arduino while toggling iris. """
    while 1:
        print 'Waiting...'
        logging.info('Waiting...')
        time.sleep(0.2)
        ser.write(char)
        if "Response" in ser.readline():
            break


def recordData(ser):
    """ Run radiometer data recording for one data block. """
    data_list = []
    times_list = []
    
    first_read = True

    # Flush input buffer
    ser.flushInput()
    count = 0

    while True:

        if not first_read:
            if (currentMicroTime() - record_start >= (data_block_time*1000000)):
                break

        try:
            b1 = ord(ser.read(1))
            b2 = ord(ser.read(1))
            #ser.flushInput()
        except:
            print "Couldn't get data!"
            logging.info("Couldn't get data!")
            continue

        # Calculate ADC value from 2 bytes transfered via COM interface
        serial_value = b1 + b2*256

        if serial_value != '':
            if first_read:

                first_read = False
                record_start = currentMicroTime()
                time_start = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S.%f")
                first = currentMicroTime()

                print 'Start', time_start
                logging.info('Start ' + str(time_start))

            #print serial_value

            # Add value to data list
            try:

                # Add the timestamp to list
                times_list.append(round((currentMicroTime() - first)/1000000.0, 6))

                # Add the measurement to list
                data_list.append(serial_value)


            except:
                print 'Error adding data to list!'
                logging.info('Error adding data to list!')

                print serial_value
                logging.info(str(serial_value))
                break

    run_duration = currentMicroTime() - record_start

    # Calculate samples per second
    sps = len(data_list) / (run_duration / 1000000.00)
    print 'Calculated SPS: ', sps
    logging.info('Calculated SPS: ' + str(sps))

    return time_start, times_list, data_list


def initConnection(port):
    """ Initialize connection to Arduino. """

    # Initalize serial connection, block read until new data is recieved
    ser = serial.Serial(port, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=None)

    # Wait for initialization
    time.sleep(2)

    # Open iris
    waitResponse(ser, "1")

    # Wait for the iris to open
    time.sleep(2)

    print 'Connected!'
    logging.info('Connected!')

    # Flush input buffer
    ser.flushInput()

    return ser

def closeConnection(ser):
    """ Close connection to Arduino. """
    print 'Ending data capture'
    logging.info('Ending data capture')

    # Close iris
    waitResponse(ser, '0')

    # Close serial communication
    ser.close()

def writeData():
    """ Write data to a file. """
    while 1:
        if not q.empty():
            data = q.get()

            night_folder = data[3]
            file_name = str(data[0]).replace(':', '.') + '.csv'
            times_array = data[1]
            data_array = data[2]
            times_array = np.array(times_array)
            data_array = np.array(data_array)
            output = np.column_stack((times_array.flatten(), data_array.flatten()))
            np.savetxt(night_folder + os.sep + file_name, output, fmt = ['%s', '%s'], delimiter = ',')
            
        time.sleep(1)



if __name__ == '__main__':

    # Define the used Arduino port
    arduino_port = 'COM4'

    # Duration of a single time block in seconds
    data_block_time = 10.24 #s

    # Initiate logging
    logging.basicConfig(filename='record_log.log', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y/%m/%d-%H:%M:%S')

    # Set a thread which writes data to files
    q = Queue.Queue()
    thread1 = threading.Thread(target=writeData)

    print 'Data block duration: ', data_block_time, 's'
    logging.info('Data block duration: ' + str(data_block_time) + 's')

    # Start the saving thread
    thread1.start()


    counter = 0

    while True:
        if counter == 0:
            start_time, duration = wordDayDuration(44.869509, 13.853925, 23)

            # Recalculate the duration to seconds from hours
            duration = duration*60*60

            # Wait if it is not yet time to start recording
            if start_time != True:

                # Calculate seconds to wait until recording
                seconds_waiting = int((start_time - datetime.datetime.now()).total_seconds()) + 1
                    
                print 'Waiting ' + str(seconds_waiting) + ' seconds.'
                logging.info('Waiting ' + str(seconds_waiting) + ' seconds.')
                time.sleep(seconds_waiting)
            
            # Generate the night folder name
            night_folder = datetime.datetime.now().strftime("%Y%m%d") + (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d")

            # Make a now night folder
            mkdirp(night_folder)
            
            counter = int(duration/data_block_time) + 1

            # Initialize connection
            ser = initConnection(arduino_port)

        
        else:
            counter -= 1
            
            # Run data recording
            time_start, times_array, data_array = recordData(ser)

            # Put files that are to be written into a file in queue so the saving thread can pick them up
            q.put((time_start, times_array, data_array, night_folder))

            # Close conection if this is the last recording run
            if counter == 0:
                closeConnection(ser)

                # Wait a bit before recalculating the new start time
                time.sleep(5*60)

