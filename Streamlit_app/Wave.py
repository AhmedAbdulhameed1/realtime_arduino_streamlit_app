import serial
import matplotlib.pyplot as plt
import time
import csv

# Set up the serial connection
ser = serial.Serial('COM5', 9600)  # Replace 'COM5' with your Arduino's serial port
time.sleep(2)

# Prepare for plotting
plt.ion()
fig, ax = plt.subplots()
x_data = []
y_data = []

# Prepare CSV file
filename = "arduino_data.csv"
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Time (s)", "Voltage (V)"])

# Function to read data from Arduino
def read_arduino():
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        return float(line)
    return None

# Loop to keep reading data from Arduino
try:
    start_time = time.time()
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        while True:
            voltage = read_arduino()
            if voltage is not None:
                current_time = time.time() - start_time
                x_data.append(current_time)
                y_data.append(voltage)
                ax.clear()
                ax.plot(x_data, y_data)
                plt.xlabel('Time (s)')
                plt.ylabel('Voltage (V)')
                plt.title('Arduino Waveform')
                plt.pause(0.01)

                # Write to CSV
                writer.writerow([current_time, voltage])
                print(f"Time: {current_time:.2f}s, Voltage: {voltage:.2f}V")
            time.sleep(0.02)
except KeyboardInterrupt:
    print("Exiting the program.")
finally:
    ser.close()
    plt.show()
