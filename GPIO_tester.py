import RPi.GPIO as GPIO
import time

# Set up GPIO
GPIO.setmode(GPIO.BCM)

# Button pin
button_pin = 18  # GPIO pin where the button is connected
relay_pins = [17, 27, 22, 23]  # GPIO pins connected to relay channels

# Set up the button pin as an input with a pull-down resistor
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Set up relay pins as output (initially off)
for pin in relay_pins:
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

# Function to test the button press and toggle relays
def test_button_and_relays():
    print("Press the button to toggle the relays.")
    while True:
        # Check the button press state
        if GPIO.input(button_pin) == GPIO.HIGH:
            print("Button pressed! Toggling relays...")
            
            # Toggle the relays (turn ON)
            for pin in relay_pins:
                GPIO.output(pin, GPIO.HIGH)
            print("Relays ON.")
            
            # Wait for 1 second
            time.sleep(1)
            
            # Toggle the relays (turn OFF)
            for pin in relay_pins:
                GPIO.output(pin, GPIO.LOW)
            print("Relays OFF.")
            
            # Wait for 1 second before checking the button again
            time.sleep(1)
        else:
            # Button is not pressed, wait for the next press
            time.sleep(0.1)

# Run the test function
try:
    test_button_and_relays()
except KeyboardInterrupt:
    print("\nTest interrupted by user.")
finally:
    # Clean up GPIO settings
    GPIO.cleanup()
