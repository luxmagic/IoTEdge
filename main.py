import paho.mqtt.client as mqtt
from crypto_mqtt import protect, unprotect
import time, secret

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker!")
    mqtt_client.subscribe(secret.MQTT_CLIENT)

def on_message(client, userdata, msg):
    payload = unprotect(msg.payload)
    print(f"Received message: {payload} on topic {msg.topic}")

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(secret.MQTT_BROKER, secret.MQTT_PORT, 60)

while mqtt_client.is_connected:
    for i in range(10):
        payload = f"{i*2}"
        mqtt_client.publish(secret.MQTT_TOPIC, protect(payload))
        print(f"[PUBLISH] {payload}")
        time.sleep(2)
    mqtt_client.loop()