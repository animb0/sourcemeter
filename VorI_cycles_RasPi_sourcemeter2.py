# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 12:21:41 2025
Keithley 2450 Voltage/Current Measurement Script (PyVISA Only)

@author: ZahndN
For Keithley sourcemeter Nr 2 borrowed from Biophysics 
"""

#

import time
import pandas as pd
from pathlib import Path
import pyvisa
# Initialize PyVISA Resource Manager
rm = pyvisa.ResourceManager()

# Connect to Keithley 2450
keithley = rm.open_resource("USB0::1510::9296::04304940::0::INSTR")
# Identify the device
print("Connected to:", keithley.query("*IDN?"))

# Get user input for experiment parameters
user_input = input(
    "Enter experiment name, measurement time (s), recharge time (s), recharge voltage (V or A), cycles, recharging limit, mode (V/I):\n"
)
experiment, measure_time, recharge_time, recharge_val, cycles, limit, mode = user_input.split()

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
    keithley.write("OUTP OFF")

    # ENABLE measurement
    keithley.write("SENS:FUNC 'VOLT','CURR'")
    keithley.write("SENS:VOLT:RANG:AUTO ON")
    keithley.write("SENS:CURR:RANG:AUTO ON")
    time.sleep(0.05)

    start_time = time.time()
    while time.time() - start_time < duration:
        try:
            if mode.lower() == 'v':
                value = float(keithley.query("MEAS:VOLT?"))
            else:
                value = float(keithley.query("MEAS:CURR?"))

            current_time = time.time() - timezero
            data.append({"Time": current_time, mode.upper(): value, "Voltage_Applied": 1})
            print(f"Measuring: Time = {round(current_time, 3)}s, {mode.upper()} = {round(value, 9)}")

        except Exception as e:
            print(f"❌ Measurement error: {e}")

        time.sleep(1)

# Function to apply voltage during recharge
def apply_voltage(keithley, data, limit, mode):
    # Configure source for voltage output
    keithley.write("SOUR:FUNC VOLT")
    keithley.write(f"SOUR:VOLT {recharge_val}")
    #keithley.write(f"SOUR:VOLT:ILIM {limit}")  # set current limit

    # Enable measurement subsystem
    keithley.write("SENS:FUNC 'VOLT','CURR'")
    keithley.write("SENS:VOLT:RANG:AUTO ON")
    keithley.write("SENS:CURR:RANG:AUTO ON")

    keithley.write("OUTP ON")
    time.sleep(0.05)  # let the SMU settle to avoid USB freeze

    start_time = time.time()
    while time.time() - start_time < recharge_time:
        try:
            value = float(
                keithley.query("MEAS:VOLT?") if mode == "v" else keithley.query("MEAS:CURR?")
            )
            current_time = time.time() - timezero

            data.append({
                "Time": current_time,
                mode.upper(): value,
                "Voltage_Applied": recharge_val
            })

            print(
                f"Applying {recharge_val}V: Time = {round(current_time, 3)}s, {mode.upper()} = {round(value, 5)}"
            )
        except Exception as e:
            print("⚠ Error during recharge:", e)

        time.sleep(1)

    keithley.write("OUTP OFF")
    time.sleep(0.05)


# Execute cycles
print(f"Total duration: {total_time}s, Mode: {mode.upper()}")
#measure before first cycle for 10 s
measure(keithley, data, 10, mode)

for cycle in range(cycles):
    print(f"Cycle {cycle + 1}/{cycles}")
    apply_voltage(keithley, data, limit, mode)
    measure(keithley, data, measure_time, mode)

# Save data to CSV in a dynamically created folder named after the experiment
current_time_str = time.strftime("%Y%m%d-%H%M")
base_folder = Path("/home/nickzahnd/Documents/Sourcemeter_Data")  # Raspberry Pi storage path
experiment_folder = base_folder / experiment  # Folder named after experiment
experiment_folder.mkdir(parents=True, exist_ok=True)  # Create folder if it doesn’t exist

limit *=1000
file_path = experiment_folder / f"{current_time_str}_{experiment}_{measure_time}s_dis_{recharge_time}s_charge_{recharge_val}_lim{limit}mAorV_{mode}.csv"

# Save data
df = pd.DataFrame(data)
df.to_csv(file_path, index=False)
print(f"Measurement finished. Data saved to {file_path}")

# Close connection
keithley.close()
print("Keithley connection closed.")
