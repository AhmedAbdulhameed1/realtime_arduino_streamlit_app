import csv
import math
import time

filename = 'wave_data.csv'
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Time (s)", "Voltage (V)"])
    
    start_time = time.time()
    for i in range(1000):  # Create 1000 data points
        current_time = time.time() - start_time
        wave_voltage = 45 * math.sin(current_time)
        writer.writerow([current_time, wave_voltage])
        time.sleep(0.01)