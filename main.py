import paho.mqtt.client as mqtt
import time

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "temperature"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker!")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Received message: {payload} on topic {msg.topic}")

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

while mqtt_client.is_connected:
    for i in range(10):
        payload = f"{i*2}°C"
        mqtt_client.publish(MQTT_TOPIC, payload)
        print(f"[PUBLISH] {payload}")
        time.sleep(2)
    mqtt_client.loop()