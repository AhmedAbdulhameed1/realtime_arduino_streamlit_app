import os
import sys
import time
import csv
import serial
import serial.tools.list_ports
import firebase_admin
from firebase_admin import credentials, db
import streamlit as st
import matplotlib.pyplot as plt

# Dynamically get the JSON file path from environment variable
json_file_path = os.getenv("FIREBASE_CREDENTIALS_PATH")

if not json_file_path:
    raise ValueError("Environment variable 'FIREBASE_CREDENTIALS_PATH' is not set or invalid.")

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(json_file_path)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://arduino-data-602d7-default-rtdb.europe-west1.firebasedatabase.app/'
    })
firebase_ref = db.reference('arduino_data')

# Streamlit UI Setup
st.title("Arduino Real-Time Data Logger")
st.subheader("Dynamic COM Port Detection")

# Function to dynamically detect COM port
@st.cache(allow_output_mutation=True)
def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Arduino" in port.description:
            return port.device
    return None

def initialize_serial_connection():
    port = find_arduino_port()
    if not port:
        st.error("No Arduino device detected. Please connect your device.")
        return None
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        st.success(f"Connected to Arduino on {port}")
        return ser
    except serial.SerialException as e:
        st.error(f"Error connecting to {port}: {e}")
        return None

baud_rate = st.number_input("Enter the Baud Rate:", value=9600, step=1)
serial_connection = None

# CSV File Setup
filename = "arduino_data.csv"
if "csv_initialized" not in st.session_state:
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time (s)", "Voltage (V)"])
    st.session_state["csv_initialized"] = True

# Initialize Session State Data
if "x_data" not in st.session_state:
    st.session_state["x_data"] = []
if "y_data" not in st.session_state:
    st.session_state["y_data"] = []

# Function to Read Data from Arduino
def read_arduino(serial_connection):
    if serial_connection.in_waiting > 0:
        line = serial_connection.readline().decode('utf-8').rstrip()
        if line:
            try:
                return float(line)
            except ValueError:
                st.warning(f"Invalid data received: {line}")
    return None

# Function to Upload Data to Firebase
def upload_to_firebase(time_value, voltage):
    firebase_ref.push({
        'time': time_value,
        'voltage': voltage
    })

# Connect to Arduino Button
if st.button("Connect to Arduino"):
    serial_connection = initialize_serial_connection()
    if serial_connection:
        start_time = time.time()
        st.subheader("Real-Time Voltage Plot")
        chart = st.empty()  # Placeholder for dynamic plot

        # Start Reading Data
        try:
            with open(filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                while True:
                    voltage = read_arduino(serial_connection)
                    if voltage is not None:
                        current_time = time.time() - start_time
                        st.session_state["x_data"].append(current_time)
                        st.session_state["y_data"].append(voltage)

                        # Write Data to CSV
                        writer.writerow([current_time, voltage])

                        # Upload Data to Firebase
                        upload_to_firebase(current_time, voltage)

                        # Plot Data
                        fig, ax = plt.subplots()
                        ax.plot(st.session_state["x_data"], st.session_state["y_data"], label="Voltage (V)")
                        ax.set_xlabel("Time (s)")
                        ax.set_ylabel("Voltage (V)")
                        ax.set_title("Arduino Real-Time Voltage")
                        ax.legend()
                        chart.pyplot(fig)

                    time.sleep(0.02)
        except Exception as e:
            st.error(f"An error occurred: {e}")
        finally:
            if serial_connection:
                serial_connection.close()
