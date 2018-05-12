import ephem
import datetime
import time
import serial
import matplotlib.pyplot as plt
import numpy as np
import threading, Queue
import logging
import os
import nightAnalyzer
import shutil
from subprocess import call

def work_day_duration(lat, lon, elevation):
    #Function that calculates start time and duration of capturing
    #Reqiured inputs: Latitude, longitude, elevation
    #Outputs: When to start recording (start_time) and for how long (duration), returned as list.
    #   start_time returns 'True' if it needs to start immediately
    #   duration returns a number of hours rounded %.2f

    o=ephem.Observer()
    o.lat=str(lat)
    o.long=str(lon)
    o.elevation=elevation
    o.horizon = '-5:26' #Correction for 30-minute later start/ending
    s=ephem.Sun()
    s.compute()

##    #Correct time for camera saturation time (about 30 min)
##    delta=datetime.timedelta(minutes=30)

    next_rise=ephem.localtime(o.next_rising(s))## - delta
    next_set=ephem.localtime(o.next_setting(s))## + delta


    current_time=datetime.datetime.now() + datetime.timedelta(hours=1)


    #print next_set
    #print next_rise

    if next_set>next_rise: #Should we start recording now?
        start_time=True
        #duration=datetime.timedelta(minutes=30)
    else:
        start_time=next_set
        #duration=duration=datetime.timedelta(minutes=0)

    if start_time==True: #For how long should we record?
        duration=next_rise-current_time
    else:
        duration=next_rise-next_set

    duration=round(duration.total_seconds()/60/60, 2)

    return (start_time, duration)

# function that returns number of millisecnds since epohe
curr_micro_time = lambda: int(round(time.time() * 1000000))

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
    #times_array = np.array([], dtype=np.float32)
    times_list = []
    

    first_read = True

    # Flush input buffer
    ser.flushInput()
    count = 0
    while 1:

        if not first_read:
            if (curr_micro_time() - record_start >= (data_block_time*1000000)):
                break

        try:
            b1 = ord(ser.read(1))
            b2 = ord(ser.read(1))
            #ser.flushInput()
        except:
            print "couldn't get data!"
            logging.info("couldn't get data!")
            continue

        # Calculate ADC value from 2 bytes transfered via COM interface
        serial_value = b1 + b2*256
        if serial_value != '':
            if first_read:
                first_read = False
                record_start = curr_micro_time()
                time_start = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S.%f")
                first = curr_micro_time()
                print 'start', time_start
                logging.info('start ' + str(time_start))

            #print serial_value

            # Add value to data list
            try:

                # Numpy arrays
                #data_array = np.append(data_array, [4096-serial_value])

                #times_array.append(datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S.%f"))
                times_list.append(round((curr_micro_time() - first)/1000000.0, 6))
                data_list.append(serial_value)


            except:
                print 'Error!'
                logging.info('Error!')
                print serial_value
                logging.info(str(serial_value))
                break

    run_duration = curr_micro_time() - record_start

    # Samples per second
    sps = len(data_list) / (run_duration / 1000000.00)
    print 'Calculated SPS: ', sps
    logging.info('Calculated SPS: ' + str(sps))

    return time_start, times_list, data_list


def initConnection(port = '/dev/ttyUSB0'):
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
            file_name = str(data[0]) + '.csv'
            times_array = data[1]
            data_array = data[2]
            times_array = np.array(times_array)
            data_array = np.array(data_array)
            output = np.column_stack((times_array.flatten(), data_array.flatten()))
            #np.savetxt(file_name.replace(':', '.'), output, fmt = ['%2.5f', '%d'], delimiter = ',')
            np.savetxt(file_name.replace(':', '.'), output, fmt = ['%s', '%s'], delimiter = ',')
        time.sleep(1)

# initiate logging
logging.basicConfig(filename='record_log_%s.log' % datetime.datetime.now(), level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y/%m/%d-%H:%M:%S')

# set a thread which writes data to files
q = Queue.Queue()
thread1 = threading.Thread(target=writeData)

# Duration of a single time block in seconds
data_block_time = 600 #s

print 'Data block duration: ', data_block_time, 's'
logging.info('Data block duration: ' + str(data_block_time) + 's')

# Start the saving thread
thread1.start()

# Initialize connection
ser = initConnection()

# used to determin whether the analizing script should be called
analyze = False
counter = 0

while True:
    if counter <= 0:
        start_time = work_day_duration(44.869509, 13.853925, 23)[0] 
        if  start_time == True:
            rising = ephem.localtime(ephem.Observer().next_rising(ephem.Sun()))
            counter = ((rising - datetime.datetime.utcnow()).total_seconds()) / data_block_time
        
        else:
            if analyze:
                print "Analyzing..."
                logging.info("Analyzing...")
                nightAnalyzer.analyze()
                analyze = False   
            print 'Waiting ' + str(int((start_time - datetime.datetime.now()).total_seconds())) + ' seconds.'
            logging.info('Waiting ' + str(int((start_time - datetime.datetime.now()).total_seconds())) + ' seconds.')
            time.sleep(int((start_time - datetime.datetime.now()).total_seconds())+60)
    
    else:
        counter -= 1
        analyze = True
        # Run data recording
        time_start, times_array, data_array = recordData(ser)

        # Put files that are to be written into a file in queue so the saving thread can pick them up
        #writeData(str(time_start) + '.csv', times_array, data_array)
        q.put((time_start, times_array, data_array))

        #print 'data' +  str(data_array)
        #logging.info('data' +  str(data_array))

    # Close connection
    #closeConnection(ser)
