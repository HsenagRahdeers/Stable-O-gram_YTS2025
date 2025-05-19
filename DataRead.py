import csv
import matplotlib.pyplot as plt
import os

# Path to the CSV file (update if different)
CSV_FILE = os.path.expanduser('~/Desktop/hx711_data2.csv')

# Lists to hold data
timestamps = []
values1, values2, values3, values4 = [], [], [], []

# Read the CSV
with open(CSV_FILE, 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        timestamps.append(int(row['timestamp_us']) / 1_000_000)  # microseconds → seconds
        values1.append(abs(int(row['value1'])))
        values2.append(abs(int(row['value2'])))
        values3.append(abs(int(row['value3'])))
        values4.append(abs(int(row['value4'])))

# Plotting
plt.figure(figsize=(12, 6))
plt.plot(timestamps, values1, label='Sensor 1')
plt.plot(timestamps, values2, label='Sensor 2')
plt.plot(timestamps, values3, label='Sensor 3')
plt.plot(timestamps, values4, label='Sensor 4')
plt.xlabel('Time (s)')
plt.ylabel('Sensor Readings')
plt.title('HX711 Load Cell Readings Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
