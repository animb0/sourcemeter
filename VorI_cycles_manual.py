#same functionality as VorI_cycles but with manual imput of parameters directly in code
import time
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from qcodes.dataset import Measurement
from qcodes.instrument_drivers.tektronix.Keithley_2450 import Keithley2450

# Initialize the Keithley instrument
keithley = Keithley2450("keithley", "USB0::0x05e6::0x2450::04616895::INSTR")
keithley.reset()
keithley.terminals("front")

# Directly set experiment parameters here
experiment = "NZ32_HNLAH_sample3"
measure_time = 2  # Measurement duration in seconds
recharge_time = 2  # Recharge time in seconds
recharge_V = 1  # Recharge voltage (1V or appropriate)
cycles = 3  # Number of cycles
total_time = measure_time * cycles + recharge_time * (cycles - 1)
timezero = time.time()

# Define mode (either 'Voltage' or 'Current')
mode = "voltage"  # Change to "Current" if you want to measure current

# Function to measure voltage or current
def measure(keithley, data, duration, mode):
    start_time = time.time()
    keithley.sense.function(mode) # Set to voltage or current measurement mode
    while time.time() - start_time < duration:
        with keithley.output_enabled.set_to(True):
            value = keithley.sense.voltage() if mode == "voltage" else keithley.sense.current()
        current_time = time.time() - timezero
        data.append({"Time": current_time, mode.capitalize(): value, "Voltage_Applied": 1})  # Add measurement type
        print(f"Time = {round(current_time, 3)}, {mode.capitalize()} = {round(value, 5)}")
        time.sleep(1)  # Measurement interval of 1 second

# Function to apply voltage
def apply_voltage(keithley, data):
    with keithley.output_enabled.set_to(True):
        keithley.source.voltage(recharge_V)
        start_time = time.time()
        while time.time() - start_time < recharge_time:
            voltage = keithley.sense.voltage()
            current_time = time.time() - timezero
            data.append({"Time": current_time, "Voltage": voltage, "Voltage_Applied": 0})
            print(f"Applying {recharge_V}V: Time = {round(current_time, 3)}, Voltage = {round(voltage, 5)}")
            time.sleep(1)  # Measurement interval of 1 second

# Executing the cycles
data = []
print("Total measurement duration:", total_time)
for cycle in range(0, cycles):
    print(f"Cycle {cycle + 1}")
    measure(keithley, data, measure_time, mode)
    if cycle < cycles - 1:  # Check if it's not the last cycle
        apply_voltage(keithley, data)

# Save data to CSV file in the user's Documents folder with timestamp in the name
current_time_str = time.strftime("%Y%m%d-%H%M%S")  # Format the current time
documents_folder = Path.home() / "Documents"  # User's Documents folder
output_folder = documents_folder / "Electronic measurements/Sourcemeter/Raw data/Python_script_cycles_output"
output_folder.mkdir(parents=True, exist_ok=True)  # Create folder if it doesn't exist
file_path = output_folder / f"{current_time_str}_{experiment}_{measure_time}s_dis_{recharge_time}s_charge_{recharge_V}V.csv"

# Save data to the file
df = pd.DataFrame(data)
df.to_csv(file_path, index=True)
print(f"Measurement finished. Data saved to {file_path}")

# Close the instrument
keithley.close()
