import serial
import requests
import time
import json

# Configure serial connection
SERIAL_PORT = "/dev/ttyACM0"  # Change if needed
BAUD_RATE = 9600
SERVER_URL = "http://172.20.10.4:5000/data"  # Web server on Raspberry Pi 1

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Wait for connection

    while True:
        if ser.in_waiting > 0:
            sensor_data = ser.readline().decode('utf-8').strip()
            print(f"Raw Data: {sensor_data}")

            # Parse sensor values from the serial output
            try:
                if "Moisture:" in sensor_data:
                    soilMoisture = int(sensor_data.split(":")[1].strip())
                elif "Humidity:" in sensor_data and "Temperature:" in sensor_data:
                    parts = sensor_data.split("|")
                    humidity = float(parts[0].split(":")[1].strip().replace("%", ""))
                    temperature = float(parts[1].split(":")[1].strip().replace("°C", ""))
                elif "Water Level:" in sensor_data:
                    floatSensorValue = int(sensor_data.split(":")[1].strip())
                elif "====" in sensor_data:  # End of sensor data group
                    # Prepare data to send
                    data = {
                        "floatSensorValue": floatSensorValue,
                        "temperature": temperature,
                        "humidity": humidity,
                        "soilMoisture": soilMoisture
                    }

                    # Send data to Raspberry Pi server
                    try:
                        response = requests.post(SERVER_URL, json=data)
                        print(f"Server Response: {response.status_code} | {response.text}")
                    except Exception as e:
                        print(f"Error sending data: {e}")

            except Exception as e:
                print(f"Error parsing data: {e}")

        time.sleep(1)

except serial.SerialException as e:
    print(f"Serial Error: {e}")

