# MeteorRadiometer
==========

The goal of this project is to make a low-cost radiometer for fireball observations.
The current goal is to have 16-bit data from a photodiode sampled at 500 Hz which would show high-frequency characteristics in the fireball's lightcurve.

You can find more information (IMC paper, presentation, schematics) in the "docs" folder. Feel free to contact me if you have any questions.

*Current status:*
Sampling the radiometer at 500 Hz with 16-bits of data. The data is recorded via a Python script, and the 10.24 seconds of recorded data (time equivalent to 256 video frames @25FPS) is saved to disk or shown on a graph.
The software scripts are still very "rough" and not user friendly. 
Some knowledge with the Arduino platform is required - so I would recommend you try out some basic Arduino stuff first if you haven't already. If you have the Arduino development software installed, you need to put the "AD770X-master" library from the Github page to "C:\Program Files\Arduino\libraries" and then upload the "MeteorRadiometerArduino.ino" to your Arduino UNO device.

Here is the link to one raw night of observations in the CSV format: https://www.dropbox.com/s/9qqequotnv5hsmf/2015082223%20Pula.7z?dl=1
You can do your own plots from the data by using the "radiometerPlot.py" plot. You need to change the "csv_directory" to tell it where it can find the raw CSV files.

When you connect the radiometer, to preview what the radiometer is recording now, you could use the "readArduino.py" script (just change to COM port).
To start recording, you need to know on which COM port your Arduino device is connected. Then edit the "radiometerRecord.py" script to use the proper COM port to connect to (currently it is COM 4 set as default in the script). To set the recording duration, you must change the "record_duration" variable to how much hours of recording you want to preform.

This project uses several different libraries:
- modified AD770X library for working with the 16-bit AD7705 ADC
- pySerial for serial communication with Arduino and Python
- numpy, scipy, matplitlib python libraries

Parts used:
- Arduino Uno R3
- AD7705 ADC board
- BPW34 photodiode and LMC6462 OP amp

Work to be done:
- pack everything into a nifty little box
- write software for fireball detection
- make the software more user friendly
