import asyncio
import websockets
import json
import subprocess
from datetime import datetime, time

# In-memory storage for schedules
schedules = []

async def handle_client(websocket, path):
    print("New client connected")
    try:
        async for message in websocket:
            data = json.loads(message)
            
            if data['type'] == 'set_schedule':
                # Add new schedule
                new_schedule = {
                    'onTime': data['schedule']['onTime'],
                    'offTime': data['schedule']['offTime']
                }
                schedules.append(new_schedule)
                
                # Forward to MQTT
                forward_to_mqtt(new_schedule)
                
                # Send updated schedules to all clients
                await broadcast_schedules()
                
            elif data['type'] == 'get_initial_data':
                # Send current schedules and status
                await websocket.send(json.dumps({
                    'type': 'schedule_update',
                    'schedules': schedules
                }))
                
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

def forward_to_mqtt(schedule):
    # Convert schedule to MQTT message format
    mqtt_message = json.dumps(schedule)
    
    # Use mosquitto_pub to send the message
    try:
        subprocess.run([
            'mosquitto_pub',
            '-h', 'localhost',  # MQTT broker address
            '-t', 'light/schedule',  # Topic
            '-m', mqtt_message
        ], check=True)
        print(f"Published to MQTT: {mqtt_message}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to publish to MQTT: {e}")

async def broadcast_schedules():
    message = json.dumps({
        'type': 'schedule_update',
        'schedules': schedules
    })
    
    # Send to all connected clients
    for websocket in websockets.WebSocketServer.clients:
        try:
            await websocket.send(message)
        except:
            pass

async def check_schedules():
    while True:
        now = datetime.now().time()
        
        # Check if it's time to turn on/off
        for schedule in schedules:
            on_time = time.fromisoformat(schedule['onTime'])
            off_time = time.fromisoformat(schedule['offTime'])
            
            if now.hour == on_time.hour and now.minute == on_time.minute:
                send_light_command('1')
            elif now.hour == off_time.hour and now.minute == off_time.minute:
                send_light_command('0')
        
        await asyncio.sleep(60)  # Check every minute

def send_light_command(state):
    try:
        subprocess.run([
            'mosquitto_pub',
            '-h', 'localhost',
            '-t', 'light/command',
            '-m', state
        ], check=True)
        print(f"Sent light command: {state}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to send light command: {e}")

async def main():
    # Start WebSocket server
    server = await websockets.serve(
        handle_client,
        "localhost",
        8765
    )
    
    # Start schedule checker
    asyncio.create_task(check_schedules())
    
    print("WebSocket server started on ws://localhost:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())