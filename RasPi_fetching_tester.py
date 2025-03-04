# -*- coding: utf-8 -*-
"""
Created on Tue Mar  4 14:25:54 2025

@author: ZahndN
"""

import time

def main():
    print("Hello from Raspberry Pi!")
    for i in range(5):
        print(f"Iteration {i+1}: The script is working!")
        time.sleep(1)
    print("Test complete.")

if __name__ == "__main__":
    main()
