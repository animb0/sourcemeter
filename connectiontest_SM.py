# -*- coding: utf-8 -*-
"""
Created on Tue Mar  4 15:18:41 2025

@author: ZahndN
"""

import pyvisa

# Initialize PyVISA
rm = pyvisa.ResourceManager()

# List available instruments
resources = rm.list_resources()
print(f"Connected Resources: {resources}")

# Check if the Keithley 2450 is found
if not resources:
    print("No instruments found! Check connections.")
else:
    for resource in resources:
        try:
            keithley = rm.open_resource(resource)
            idn = keithley.query("*IDN?")  # Query the instrument identification
            print(f"Instrument at {resource}: {idn}")
            keithley.close()
        except Exception as e:
            print(f"Could not communicate with {resource}: {e}")
