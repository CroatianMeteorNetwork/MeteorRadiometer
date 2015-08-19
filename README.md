# MeteorRadiometer
==========

The goal of this project is to make a low-cost radiometer for fireball observations.
The current goal is to have 16-bit data from a photodiode sampled at 500 Hz which would show high-frequency characteristics in the fireball's lightcurve.

*Current status:*
Sampling the radiometer at 500 Hz with 16-bits of data. The data is recorded via a Python script, and the 10.24 seconds of recorded data (time equivalent to 256 video frames @25FPS) is saved to disk or shown on a graph. The solenoid is activated during the recording peroid via the relay shield.

This project uses several different libraries:
- modified AD770X library for working with the 16-bit AD7705 ADC
- pySerial for serial communication with Arduino and Python

Parts used:
- Arduino Uno R3
- AD7705 ADC board
- ZYE1-0837ZP solenoid (cues during the day to protect the photodiode from the Sun)
- Arduino relay shield for switching on the solenoid
- BPW34 photodiode and LMC6462 OP

Work to be done:
- design a small metal arm which would be deployed during the day to protect the photodiode from the Sun
- finish the prototype and design a PCB -> solder the components
- pack everything into a nifty little box
- write software for fireball detection
