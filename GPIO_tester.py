from gpiozero import Button, OutputDevice
from signal import pause
import time

# Pin configuration
button_pin = 17  # GPIO pin for the button
relay1_pin = 27  # GPIO pin for relay 1
relay2_pin = 22  # GPIO pin for relay 2

# Initialize button and relays
button = Button(button_pin, pull_up=False)  # Button with pull-down configuration
relay1 = OutputDevice(relay1_pin, active_high=True, initial_value=False)
relay2 = OutputDevice(relay2_pin, active_high=True, initial_value=False)

# Define relay control functions
def toggle_relays():
    print("Button pressed! Toggling relays.")
    if not relay1.value:  # If relay 1 is off, turn both on
        relay1.on()
        relay2.on()
        print("Relays turned ON.")
    else:  # If relay 1 is on, turn both off
        relay1.off()
        relay2.off()
        print("Relays turned OFF.")

# Attach the button press event to the toggle function
button.when_pressed = toggle_relays

# Keep the program running
print("System is ready. Press the button to toggle relays.")
pause()
