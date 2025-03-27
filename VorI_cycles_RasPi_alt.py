# -*- coding: utf-8 -*-
"""
Keithley 2450 Voltage/Current Measurement Script (PyVISA Only)
Author: ZahndN
Date: March 2025
"""

import time
import pandas as pd
from pathlib import Path
import pyvisa

# Initialize PyVISA Resource Manager
rm = pyvisa.ResourceManager()

# Connect to Keithley 2450
keithley = rm.open_resource("USB0::0x05e6::0x2450::04616895::INSTR")

# Identify the device
print("Connected to:", keithley.query("*IDN?"))

# Get user input for experiment parameters
user_input = input(
    "Enter experiment name, measurement time (s), recharge time (s), recharge voltage (V or A), cycles, mode (V/I):\n"
)
experiment, measure_time, recharge_time, recharge_val, cycles, mode = user_input.split()

# Convert inputs to correct types
measure_time = float(measure_time)
recharge_time = float(recharge_time)
recharge_val = float(recharge_val)
cycles = int(cycles)
mode = mode.lower()

# Validate mode
if mode not in ["v", "i"]:
    print("Error: Mode must be 'V' (voltage) or 'I' (current).")
    exit()

# Set measurement mode
keithley.write(f"SENS:FUNC '{'VOLT' if mode == 'v' else 'CURR'}'")

# Prepare for measurement
total_time = measure_time * cycles + recharge_time * (cycles - 1)
timezero = time.time()
data = []

# Function to measure voltage or current
def measure(keithley, data, duration, mode):
    start_time = time.time()
    while time.time() - start_time < duration:
        value = float(keithley.query("MEAS:VOLT?") if mode == "v" else keithley.query("MEAS:CURR?"))
        current_time = time.time() - timezero
        data.append({"Time": current_time, mode.upper(): value, "Voltage_Applied": 1})
        print(f"Measuring: Time = {round(current_time, 3)}s, {mode.upper()} = {round(value, 9)}")
        time.sleep(1)

# Function to apply voltage during recharge
def apply_voltage(keithley, data, mode):
    keithley.write(f"SOUR:VOLT {recharge_val}")  # Set recharge voltage
    start_time = time.time()
    while time.time() - start_time < recharge_time:
        value = float(keithley.query("MEAS:VOLT?") if mode == "v" else keithley.query("MEAS:CURR?"))
        current_time = time.time() - timezero
        data.append({"Time": current_time, mode.upper(): value, "Voltage_Applied": 0})
        print(f"Applying {recharge_val}V: Time = {round(current_time, 3)}s, {mode.upper()} = {round(value, 5)}")
        time.sleep(1)

# Execute cycles
print(f"Total duration: {total_time}s, Mode: {mode.upper()}")
for cycle in range(cycles):
    print(f"Cycle {cycle + 1}/{cycles}")
    apply_voltage(keithley, data, mode)
    measure(keithley, data, measure_time, mode)

# Save data to CSV in a dynamically created folder named after the experiment
current_time_str = time.strftime("%Y%m%d-%H%M")
base_folder = Path("/home/pi/Documents/Sourcemeter_Data")  # Raspberry Pi storage path
experiment_folder = base_folder / experiment  # Folder named after experiment
experiment_folder.mkdir(parents=True, exist_ok=True)  # Create folder if it doesn’t exist

file_path = experiment_folder / f"{current_time_str}_{experiment}_{measure_time}s_dis_{recharge_time}s_charge_{recharge_val}_{mode}.csv"

# Save data
df = pd.DataFrame(data)
df.to_csv(file_path, index=False)
print(f"Measurement finished. Data saved to {file_path}")

# Close connection
keithley.close()
print("Keithley connection closed.")
