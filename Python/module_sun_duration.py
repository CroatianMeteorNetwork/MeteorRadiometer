import ephem
import datetime

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
    
    
    current_time=datetime.datetime.now()

    
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
    

def checkRep():
    
    print work_day_duration(45.6667, 18.4167, 90)


#checkRep()
