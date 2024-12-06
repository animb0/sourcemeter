# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import filedialog, Tk

def plot_results():
    # Open a file dialog to select the CSV file
    root = Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(
        title="Select Measurement CSV File",
        filetypes=[("CSV Files", "*.csv")]
    )
    if not file_path:
        print("No file selected. Exiting.")
        return

    # Load the CSV data
    data = pd.read_csv(file_path)

    # Ensure required columns are present
    required_columns = ["Time", "Voltage_Applied"]
    if "Voltage" in data.columns:
        mode = "Voltage"
        required_columns.append("Voltage")
    elif "Current" in data.columns:
        mode = "Current"
        required_columns.append("Current")
    else:
        print("Error: The CSV file must contain 'Voltage' or 'Current' column.")
        return

    for col in required_columns:
        if col not in data.columns:
            print(f"Error: The column '{col}' is missing in the CSV file.")
            return

    # Split data into applied and measurement segments
    applied_mask = data["Voltage_Applied"] == 0  # Rows during recharge phase
    measure_mask = data["Voltage_Applied"] == 1  # Rows during measurement phase

    # Separate segments for plotting
    applied_segments = data[applied_mask]
    measurement_segments = data[measure_mask]

    # Identify separate measurement cycles
    measurement_cycles = []
    current_cycle = []
    for i, row in measurement_segments.iterrows():
        if current_cycle and row["Time"] < current_cycle[-1]["Time"]:
            # Start a new cycle if the time decreases (or resets)
            measurement_cycles.append(pd.DataFrame(current_cycle))
            current_cycle = []
        current_cycle.append(row)

    if current_cycle:  # Add the last cycle
        measurement_cycles.append(pd.DataFrame(current_cycle))

    # Create a figure
    plt.figure(figsize=(10, 6))

    # Plot applied voltage/current segments
    plt.scatter(
        applied_segments["Time"],
        applied_segments[mode],
        color="red",
        label=f"{mode} During Applied Voltage",
        alpha=0.7,
    )

    # Plot each measurement cycle separately
    for i, cycle_data in enumerate(measurement_cycles):
        plt.plot(
            cycle_data["Time"],
            cycle_data[mode],
            label=f"Measurement Cycle {i + 1}",
            linestyle="-",
            alpha=0.7,
        )

    # Customize plot
    plt.title(f"{mode} vs. Time")
    plt.xlabel("Time (s)")
    plt.ylabel(f"{mode} (V or A)")
    plt.legend()
    plt.grid(True)

    # Show plot
    plt.show()

# Run the plot function
if __name__ == "__main__":
    plot_results()
