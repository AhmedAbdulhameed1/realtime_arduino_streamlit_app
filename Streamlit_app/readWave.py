import serial
import matplotlib.pyplot as plt
import time
import csv
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db

# Set up Firebase Admin SDK
cred = credentials.Certificate(f"arduino-data-602d7-firebase-adminsdk-wruda-6fa1491a50.json")  # Credentials JSON file path
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://arduino-data-602d7-default-rtdb.europe-west1.firebasedatabase.app/'  # Database URL
})

# Set up serial communication
try:
    ser = serial.Serial('COM5', 9600, timeout=1)  # The Arduino port
    time.sleep(2)  # Allow time for the connection to stabilize
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    exit()

# Prepare for live plotting
plt.ion()
fig, ax = plt.subplots()
x_data = []
y_data = []

# Function to read data from Arduino
def read_arduino():
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            return float(line) if line else None
    except ValueError as e:
        print(f"Error converting serial data to float: {e}")
        return None
    return None

# Function to read waveform data from a file
def read_wave_from_file(file_path, current_time):
    try:
        df = pd.read_csv(file_path)
        closest_row = df[df['Time (s)'] >= current_time].iloc[0]
        return float(closest_row['Voltage (V)'])
    except (IOError, ValueError, IndexError) as e:
        print(f"Error reading waveform data: {e}")
        return 0.0

# Function to upload data to Firebase
def upload_to_firebase(time, voltage):
    try:
        ref = db.reference('sensor_data')  # Firebase database reference
        ref.push({
            'time': time,
            'voltage': voltage
        })
        print(f"Uploaded to Firebase: Time={time}, Voltage={voltage}")
    except Exception as e:
        print(f"Error uploading to Firebase: {e}")

# Main loop
try:
    start_time = time.time()
    while True:
        arduino_voltage = read_arduino()
        if arduino_voltage is not None:
            current_time = time.time() - start_time
            wave_voltage = read_wave_from_file('wave_data.csv', current_time)  # Replace with your actual file
            total_voltage = arduino_voltage + wave_voltage

            # Update data for plotting
            x_data.append(current_time)
            y_data.append(total_voltage)
            ax.clear()
            ax.plot(x_data, y_data)
            plt.xlabel('Time (s)')
            plt.ylabel('Voltage (V)')
            plt.title('Combined Arduino and Waveform Data')
            plt.pause(0.01)

            # Upload to Firebase
            upload_to_firebase(current_time, total_voltage)

            print(f"Time: {current_time:.2f}s, Total Voltage: {total_voltage:.2f}V")
        else:
            print("No valid data received from Arduino.")

        time.sleep(0.02)
except KeyboardInterrupt:
    print("Exiting the program.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    ser.close()
    plt.show()
