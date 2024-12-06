# -*- coding: utf-8 -*-

# For the Keithley Sourcemeter 2450
# Cycles of measuring voltage or current and recharging with a source voltage
import time
import pandas as pd
from pathlib import Path  # Import pathlib for dynamic file paths
from qcodes.instrument_drivers.tektronix.Keithley_2450 import Keithley2450
import tkinter as tk
from tkinter import simpledialog, messagebox

# Initialize the Keithley instrument
keithley = Keithley2450("keithley", "USB0::0x05e6::0x2450::04616895::INSTR")

keithley.reset()
keithley.terminals("front")

# GUI for user inputs
def get_parameters():
    # Create a Tkinter root window
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Get user inputs
    experiment = simpledialog.askstring("Experiment Name", "Enter the experiment name:")
    measure_time = simpledialog.askfloat("Measurement Time", "Enter the measurement time (seconds):", minvalue=0.1)
    recharge_time = simpledialog.askfloat("Recharge Time", "Enter the recharge time (seconds):", minvalue=0.1)
    recharge_V = simpledialog.askfloat("Recharge Voltage", "Enter the recharge voltage (V):")
    cycles = simpledialog.askinteger("Cycles", "Enter the number of cycles:", minvalue=1)
    mode = simpledialog.askstring("Mode", "Enter the mode (voltage or current):", initialvalue="current").lower()

    # Ensure the user enters a valid mode
    if mode not in ["voltage", "current"]:
        messagebox.showerror("Invalid Mode", "Please enter 'voltage' or 'current' as the mode.")
        root.destroy()
        exit()

    root.destroy()
    return experiment, measure_time, recharge_time, recharge_V, cycles, mode

# Get parameters from user
experiment, measure_time, recharge_time, recharge_V, cycles, mode = get_parameters()

total_time = measure_time * cycles + recharge_time * (cycles - 1)
timezero = time.time()

# Generic function to measure voltage or current
def measure(keithley, data, duration, mode):
    start_time = time.time()
    keithley.sense.function(mode)  # Set to voltage or current measurement mode
    while time.time() - start_time < duration:
        with keithley.output_enabled.set_to(True):
            value = keithley.sense.voltage() if mode == "voltage" else keithley.sense.current()
        current_time = time.time() - timezero
        data.append({"Time": current_time, mode.capitalize(): value, "Voltage_Applied": 1})  # Add measurement type
        print(f"Time = {round(current_time, 3)}, {mode.capitalize()} = {round(value, 5)}")
        time.sleep(1)  # Measurement interval of 1 second

# Function to apply voltage during recharge
def apply_voltage(keithley, data, mode):
    keithley.source.voltage(recharge_V)  # Set source voltage
    with keithley.output_enabled.set_to(True):
        start_time = time.time()
        while time.time() - start_time < recharge_time:
            value = keithley.sense.voltage() if mode == "voltage" else keithley.sense.current()
            current_time = time.time() - timezero
            data.append({"Time": current_time, mode.capitalize(): value, "Voltage_Applied": 0})
            print(f"Applying {recharge_V}V: Time = {round(current_time, 3)}, {mode.capitalize()} = {round(value, 5)}")
            time.sleep(1)  # Measurement interval of 1 second

# Executing the cycles
data = []
print(f"Total measurement duration: {total_time}s, Mode: {mode.capitalize()}")
for cycle in range(0, cycles):
    print(f"Cycle {cycle + 1}/{cycles}")
    measure(keithley, data, measure_time, mode)
    if cycle < cycles - 1:  # Check if it's not the last cycle
        apply_voltage(keithley, data, mode)

# Save data to CSV file in the user's Documents folder with timestamp in the name
current_time_str = time.strftime("%Y%m%d-%H%M%S")  # Format the current time
documents_folder = Path.home() / "Documents"  # User's Documents folder
output_folder = documents_folder / "Electronic measurements/Sourcemeter/Raw data/Python_script_cycles_output"
output_folder.mkdir(parents=True, exist_ok=True)  # Create folder if it doesn't exist
file_path = output_folder / f"{current_time_str}_{experiment}_{measure_time}s_dis_{recharge_time}s_charge_{recharge_V}V_{mode}.csv"

# Save data to the file
df = pd.DataFrame(data)
df.to_csv(file_path, index=True)
print(f"Measurement finished. Data saved to {file_path}")

# Close the instrument
keithley.close()
