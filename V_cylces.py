# For the Keithley Sourcemeter 2450
# Cycles of measuring voltage and recharging with a source voltage
import time
import pandas as pd
import matplotlib.pyplot as plt
from qcodes.dataset import (
    Measurement,
    initialise_database,
    new_experiment,
    plot_dataset,
)
from qcodes.instrument_drivers.tektronix.Keithley_2450 import Keithley2450

keithley = Keithley2450("keithley", "USB0::0x05e6::0x2450::04616895::INSTR")

keithley.reset()
keithley.terminals("front")

experiment= "NZ32_HNLAH_sample3"
measure_time = 1500
recharge_time = 1500
recharge_V = +1
cycles = 5
total_time= measure_time*cycles+recharge_time*(cycles-1)
timezero=time.time()


# Function to measure voltage
def measure_voltage(keithley, data, duration):
    start_time = time.time()
    while time.time() - start_time < duration:
        voltage = keithley.sense.function("voltage")
        with keithley.output_enabled.set_to(True):
            voltage = keithley.sense.voltage()
        current_time = time.time()-timezero
        data.append({"Time": current_time, "Voltage": voltage, "Voltage_Applied": 1})#Voltage_Applied for colour coding in plot
        print(f"Time = {round(current_time,3)}, Voltage = {round(voltage,5)}")
        time.sleep(1)  # Measurement interval of 1 second

# Function to apply voltage
def apply_voltage(keithley, data):
    with keithley.output_enabled.set_to(True):
        keithley.source.voltage(recharge_V)
        start_time = time.time()
        while time.time() - start_time < recharge_time:
            voltage = keithley.sense.voltage()
            current_time = time.time()-timezero
            data.append({"Time": current_time, "Voltage": voltage, "Voltage_Applied": 0})
            print(f"Applying {recharge_V}V: Time = {round(current_time,3)}, Voltage = {round(voltage,5)}")
            time.sleep(1)  # Measurement interval of 1 second

# Executing the cycles
data = []
print("Total measurement duration:", total_time)
for cycle in range(0, cycles):
    print("Cycle", cycle)
    measure_voltage(keithley, data, measure_time)
    if cycle < cycles-1:  # Check if it's not the last cycle
        apply_voltage(keithley, data)

        

# Save data to CSV file in desired folder and with timestamp in name
current_time_str = time.strftime("%Y%m%d-%H%M%S")  # Format the current time
file_path = f"C:/Users/ZahndN/Documents/Electronic measurements/Sourcemeter/Raw data/Python_script_cycles_output/{current_time_str}_{experiment}_{measure_time}s_dis_{recharge_time}s_charge_{recharge_V}V.csv"
df = pd.DataFrame(data)
df.to_csv(file_path, index=True)
print("Measurement finished")
keithley.close()