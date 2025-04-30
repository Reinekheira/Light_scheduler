import paho.mqtt.client as mqtt
import serial
import json
from datetime import datetime, time

# Serial connection to Arduino
try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    print("Connected to Arduino")
except serial.SerialException:
    print("Failed to connect to Arduino")
    ser = None

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    client.subscribe("light/#")

def on_message(client, userdata, msg):
    print(f"Received message on {msg.topic}: {msg.payload.decode()}")
    
    if msg.topic == "light/command":
        # Direct command (1 or 0)
        command = msg.payload.decode()
        send_to_arduino(command)
    elif msg.topic == "light/schedule":
        # Schedule received
        try:
            schedule = json.loads(msg.payload.decode())
            print(f"New schedule: ON at {schedule['onTime']}, OFF at {schedule['offTime']}")
        except json.JSONDecodeError:
            print("Invalid schedule format")

def send_to_arduino(command):
    if ser and ser.is_open:
        try:
            ser.write(command.encode())
            print(f"Sent to Arduino: {command}")
        except serial.SerialException as e:
            print(f"Failed to send to Arduino: {e}")
    else:
        print("No Arduino connection")

# Setup MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect("localhost", 1883, 60)
    print("Connected to MQTT broker")
except ConnectionRefusedError:
    print("Failed to connect to MQTT broker")

# Start the loop
client.loop_forever()