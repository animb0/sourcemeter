from gpiozero.pins.native import NativeFactory
from gpiozero import Device
Device.pin_factory = NativeFactory()
from gpiozero import Button, OutputDevice
from signal import pause
from qcodes.instrument_drivers.tektronix.Keithley_2450 import Keithley2450
import time
import pandas as pd
from pathlib import Path

# GPIO pin configuration
button_pin = 2  # Button to start measurement
relay1_pin = 27  # Relay 1 control pin
relay2_pin = 22  # Relay 2 control pin

# Initialize GPIO components
button = Button(button_pin, pull_up=False)  # Button with pull-down configuration
relay1 = OutputDevice(relay1_pin, active_high=True, initial_value=False)
relay2 = OutputDevice(relay2_pin, active_high=True, initial_value=False)

# User inputs for relay 2 switching intervals
relay2_intervals = []
while True:
    try:
        interval = input("Enter a time (in seconds) to switch relay 2, or type 'done' to finish: ")
        if interval.lower() == 'done':
            break
        relay2_intervals.append(float(interval))
    except ValueError:
        print("Invalid input. Please enter a number or 'done'.")

relay2_intervals.sort()  # Ensure intervals are in ascending order
print(f"Relay 2 will switch at these intervals: {relay2_intervals} seconds.")

# Keithley Sourcemeter configuration
keithley = Keithley2450("keithley", "USB0::0x05e6::0x2450::04616895::INSTR")
keithley.reset()
keithley.terminals("front")
mode = "voltage"  # Change to "current" for current measurement

if mode == "voltage":
    keithley.sense.function("voltage")
    keithley.sense.voltage.range(10)
elif mode == "current":
    keithley.sense.function("current")
    keithley.sense.current.range(1e-3)
else:
    raise ValueError("Invalid mode. Choose 'voltage' or 'current'.")

# Data storage
data = []
timezero = None

def measure():
    global timezero
    timezero = time.time()
    relay1.on()  # Turn on relay 1
    print("Measurement started.")

    for interval in relay2_intervals:
        next_switch_time = timezero + interval

        while time.time() < next_switch_time:
            # Perform measurement
            current_time = time.time() - timezero
            if mode == "voltage":
                measurement = keithley.sense.voltage()
            elif mode == "current":
                measurement = keithley.sense.current()

            data.append({"Time": current_time, "Measurement": measurement})
            print(f"Time: {current_time:.2f}s, {mode.capitalize()}: {measurement:.6f}")
            time.sleep(1)  # Measurement interval

        # Toggle relay 2
        relay2.toggle()
        print(f"Relay 2 toggled at {interval:.2f} seconds.")

    # Continue measurement for 10 seconds after last interval
    end_time = timezero + relay2_intervals[-1] + 10
    while time.time() < end_time:
        current_time = time.time() - timezero
        if mode == "voltage":
            measurement = keithley.sense.voltage()
        elif mode == "current":
            measurement = keithley.sense.current()

        data.append({"Time": current_time, "Measurement": measurement})
        print(f"Time: {current_time:.2f}s, {mode.capitalize()}: {measurement:.6f}")
        time.sleep(1)

    relay1.off()  # Turn off relay 1
    print("Measurement completed.")

    # Save data
    save_data()

def save_data():
    global data
    # Save data to CSV
    documents_folder = Path.home() / "Documents"
    output_folder = documents_folder / "Sourcemeter_decay"
    output_folder.mkdir(parents=True, exist_ok=True)

    current_time_str = time.strftime("%Y%m%d-%H%M%S")
    file_name = output_folder / f"{current_time_str}_measurement.csv"

    df = pd.DataFrame(data)
    df.to_csv(file_name, index=False)
    print(f"Data saved to {file_name}")

# Attach the button press event to the measure function
button.when_pressed = measure

print("System ready. Press the button to start the measurement.")
pause()
