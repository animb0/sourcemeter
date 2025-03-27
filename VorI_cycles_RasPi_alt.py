
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 12 13:10:26 2025

@author: ZahndN
"""

# -*- coding: utf-8 -*-
# For the Keithley Sourcemeter 2450 on Raspberry Pi
# Cycles of measuring voltage or current and recharging with a source voltage

import time
import pandas as pd
import pyvisa
from pathlib import Path
from qcodes.instrument_drivers.tektronix.Keithley_2450 import Keithley2450

# Initialize the Keithley instrument
#rm = pyvisa.ResourceManager()
rm = pyvisa.ResourceManager()

#keithley = rm.open_resource("USB0::0x05e6::0x2450::04616895::INSTR")
keithley = rm.open_resource("USB0::0x05e6::0x2450::04616895::INSTR")
keithley.reset()
keithley.terminals("front")

# Get user input in a single line
user_input = input("Enter experiment name, measurement time (s), recharge time (s), recharge voltage (V or A), cycles, mode (V/I):\n")
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

total_time = measure_time * cycles + recharge_time * (cycles - 1)
timezero = time.time()

# Function to measure voltage or current
def measure(keithley, data, duration, mode):
    start_time = time.time()
    keithley.sense.function(mode)  # Set mode
    while time.time() - start_time < duration:
        with keithley.output_enabled.set_to(True):
            value = keithley.sense.voltage() if mode == "v" else keithley.sense.current()
        current_time = time.time() - timezero
        data.append({"Time": current_time, mode.upper(): value, "Voltage_Applied": 1})
        print(f"Applying {recharge_val}A: Time = {round(current_time, 3)}, {mode.upper()} = {round(value, 9)}")
        time.sleep(1)

# Function to apply voltage during recharge
def apply_voltage(keithley, data, mode):
    keithley.source.voltage(recharge_val)
    with keithley.output_enabled.set_to(True):
        start_time = time.time()
        while time.time() - start_time < recharge_time:
            value = keithley.sense.voltage() if mode == "v" else keithley.sense.current()
            current_time = time.time() - timezero
            data.append({"Time": current_time, mode.upper(): value, "Voltage_Applied": 0})
            print(f"Applying {recharge_val}V: Time = {round(current_time, 3)}, {mode.upper()} = {round(value, 5)}")
            time.sleep(1)

# Execute cycles
data = []
print(f"Total measurement duration: {total_time}s, Mode: {mode.upper()}")
for cycle in range(cycles):
    print(f"Cycle {cycle + 1}/{cycles}")
    apply_voltage(keithley, data, mode)
    measure(keithley, data, measure_time, mode)

# Save data to CSV in a dynamically created folder named after the experiment
current_time_str = time.strftime("%Y%m%d-%H%M")
base_folder = Path("/home/pi/Documents/Sourcemeter_Data")  # Raspberry Pi storage path
experiment_folder = base_folder / experiment  # Folder named after experiment
experiment_folder.mkdir(parents=True, exist_ok=True)  # Create if it doesn't exist

file_path = experiment_folder / f"{current_time_str}_{experiment}_{measure_time}s_dis_{recharge_time}s_charge_{recharge_val}_{mode}.csv"

# Save data
df = pd.DataFrame(data)
df.to_csv(file_path, index=True)
print(f"Measurement finished. Data saved to {file_path}")

# Close instrument
keithley.close()
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 12 13:10:26 2025

@author: ZahndN
"""

# -*- coding: utf-8 -*-
# For the Keithley Sourcemeter 2450 on Raspberry Pi
# Cycles of measuring voltage or current and recharging with a source voltage

import time
import pandas as pd
import pyvisa
from pathlib import Path
from qcodes.instrument_drivers.tektronix.Keithley_2450 import Keithley2450

# Initialize the Keithley instrument
rm = pyvisa.ResourceManager()

keithley = rm.open_resource("USB0::0x05e6::0x2450::04616895::INSTR")
keithley.reset()
keithley.terminals("front")

# Get user input in a single line
user_input = input("Enter experiment name, measurement time (s), recharge time (s), recharge voltage (V or A), cycles, mode (V/I):\n")
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

total_time = measure_time * cycles + recharge_time * (cycles - 1)
timezero = time.time()

# Function to measure voltage or current
def measure(keithley, data, duration, mode):
    start_time = time.time()
    keithley.sense.function(mode)  # Set mode
    while time.time() - start_time < duration:
        with keithley.output_enabled.set_to(True):
            value = keithley.sense.voltage() if mode == "v" else keithley.sense.current()
        current_time = time.time() - timezero
        data.append({"Time": current_time, mode.upper(): value, "Voltage_Applied": 1})
        print(f"Applying {recharge_val}A: Time = {round(current_time, 3)}, {mode.upper()} = {round(value, 9)}")
        time.sleep(1)

# Function to apply voltage during recharge
def apply_voltage(keithley, data, mode):
    keithley.source.voltage(recharge_val)
    with keithley.output_enabled.set_to(True):
        start_time = time.time()
        while time.time() - start_time < recharge_time:
            value = keithley.sense.voltage() if mode == "v" else keithley.sense.current()
            current_time = time.time() - timezero
            data.append({"Time": current_time, mode.upper(): value, "Voltage_Applied": 0})
            print(f"Applying {recharge_val}V: Time = {round(current_time, 3)}, {mode.upper()} = {round(value, 5)}")
            time.sleep(1)

# Execute cycles
data = []
print(f"Total measurement duration: {total_time}s, Mode: {mode.upper()}")
for cycle in range(cycles):
    print(f"Cycle {cycle + 1}/{cycles}")
    apply_voltage(keithley, data, mode)
    measure(keithley, data, measure_time, mode)

# Save data to CSV in a dynamically created folder named after the experiment
current_time_str = time.strftime("%Y%m%d-%H%M")
base_folder = Path("/home/pi/Documents/Sourcemeter_Data")  # Raspberry Pi storage path
experiment_folder = base_folder / experiment  # Folder named after experiment
experiment_folder.mkdir(parents=True, exist_ok=True)  # Create if it doesn't exist

file_path = experiment_folder / f"{current_time_str}_{experiment}_{measure_time}s_dis_{recharge_time}s_charge_{recharge_val}_{mode}.csv"

# Save data
df = pd.DataFrame(data)
df.to_csv(file_path, index=True)
print(f"Measurement finished. Data saved to {file_path}")

# Close instrument
keithley.close()
