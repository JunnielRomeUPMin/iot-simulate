import json
import random
import time
from datetime import datetime
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
from flask import Flask
import threading

# Create Flask app
app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# ThingsBoard MQTT settings
THINGSBOARD_HOST = os.environ.get('THINGSBOARD_HOST', 'localhost')
THINGSBOARD_PORT = int(os.environ.get('THINGSBOARD_PORT', '1883'))
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', '059YNB54WwnoiwFixpQ9')
PORT = int(os.environ.get('PORT', '10000'))

# MQTT client setup
client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)

@app.route('/')
def health_check():
    return {"status": "healthy", "message": "IoT simulation is running"}

def run_flask():
    app.run(host='0.0.0.0', port=PORT)

def connect_to_thingsboard():
    try:
        client.connect(THINGSBOARD_HOST, THINGSBOARD_PORT, 60)
        logger.info(f"Connected to ThingsBoard at {THINGSBOARD_HOST}:{THINGSBOARD_PORT}")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to ThingsBoard: {e}")
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
                logger.info(f"Data published successfully: {payload}")
            else:
                logger.error(f"Failed to publish data: {result.rc}")
                
        except Exception as e:
            logger.error(f"Error publishing data: {e}")
            
        # Wait for 5 seconds before next reading
        time.sleep(5)

def main():
    logger.info("Starting IoT Device Simulator for Durian Farm...")
    logger.info("Simulating temperature, humidity, soil pH, and soil moisture sensors")
    
    if not all([THINGSBOARD_HOST, THINGSBOARD_PORT, ACCESS_TOKEN]):
        logger.error("Missing required environment variables!")
        logger.info("Please set THINGSBOARD_HOST, THINGSBOARD_PORT, and ACCESS_TOKEN")
        return
    
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    if connect_to_thingsboard():
        client.loop_start()
        try:
            publish_data()
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            client.loop_stop()
            client.disconnect()
            logger.info("Simulator stopped successfully")
    else:
        logger.error("Failed to start the simulator due to connection error")

if __name__ == "__main__":
    main()
