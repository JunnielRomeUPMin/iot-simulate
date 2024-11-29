import json
import random
import time
from datetime import datetime
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# ThingsBoard MQTT settings
THINGSBOARD_HOST = os.getenv('THINGSBOARD_HOST', 'localhost')
THINGSBOARD_PORT = int(os.getenv('THINGSBOARD_PORT', 1883))
ACCESS_TOKEN = '059YNB54WwnoiwFixpQ9'

# MQTT client setup
client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)

def connect_to_thingsboard():
    try:
        client.connect(THINGSBOARD_HOST, THINGSBOARD_PORT, 60)
        print(f"Connected to ThingsBoard at {THINGSBOARD_HOST}:{THINGSBOARD_PORT}")
        return True
    except Exception as e:
        print(f"Failed to connect to ThingsBoard: {e}")
        return False

def generate_sensor_data():
    """Generate random sensor data including temperature, humidity, soil pH, and soil moisture"""
    # Soil moisture typically ranges from 0% (completely dry) to 100% (saturated)
    # For durian trees, optimal soil moisture is typically between 50-80%
    # Optimal soil pH for durian trees is between 5.0 and 6.5
    return {
        "temperature": round(random.uniform(20, 30), 2),  # Temperature in Celsius
        "humidity": round(random.uniform(40, 60), 2),     # Air humidity in %
        "soilPH": round(random.uniform(4.5, 7.0), 2),    # Soil pH level
        "soilMoisture": round(random.uniform(45, 85), 2), # Soil moisture in %
        "timestamp": datetime.now().isoformat()
    }

def publish_data():
    """Publish sensor data to ThingsBoard"""
    while True:
        try:
            sensor_data = generate_sensor_data()
            # Convert data to JSON string
            payload = json.dumps(sensor_data)
            
            # Publish to ThingsBoard
            result = client.publish('v1/devices/me/telemetry', payload)
            
            if result.rc == 0:
                print(f"Data published successfully: {payload}")
            else:
                print(f"Failed to publish data: {result.rc}")
                
        except Exception as e:
            print(f"Error publishing data: {e}")
            
        # Wait for 5 seconds before next reading
        time.sleep(5)

def main():
    print("Starting IoT Device Simulator for Durian Farm...")
    print("Simulating temperature, humidity, soil pH, and soil moisture sensors")
    print("Press Ctrl+C to stop the simulator")
    
    if connect_to_thingsboard():
        client.loop_start()
        try:
            publish_data()
        except KeyboardInterrupt:
            print("\nStopping the simulator...")
        finally:
            client.loop_stop()
            client.disconnect()
            print("Simulator stopped successfully")
    else:
        print("Failed to start the simulator due to connection error")

if __name__ == "__main__":
    main()
