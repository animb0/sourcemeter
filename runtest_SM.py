# -*- coding: utf-8 -*-
"""
Created on Tue Mar  4 15:24:42 2025

@author: ZahndN
"""

import pyvisa
import time

# Initialize the Resource Manager
rm = pyvisa.ResourceManager()

# Open a connection to the Keithley 2450
keithley = rm.open_resource("USB0::0x05e6::0x2450::04616895::INSTR")

# Identify the device
print("Device ID:", keithley.query("*IDN?"))

# Set to voltage measurement mode
keithley.write("SENS:FUNC 'VOLT'")  # Select voltage measurement

# Wait for settings to take effect
time.sleep(0.5)

print("\nMeasuring Voltage...")

# Measure voltage every second for 5 seconds
for i in range(5):
    voltage = keithley.query("MEAS:VOLT?")  # Read voltage
    print(f"Reading {i+1}: {voltage.strip()} V")  # Print voltage
    time.sleep(1)

# Close connection
keithley.close()
print("\nMeasurement complete. Connection closed.")
