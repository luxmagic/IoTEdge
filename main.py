import paho.mqtt.client as mqtt
from fastapi import FastAPI

app = FastAPI()

# MQTT config
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "iot/data"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker!")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Received message: {payload} on topic {msg.topic}")
    # Тут можно сохранять в базу, отправлять WebSocket и т.п.

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

@app.on_event("startup")
def start_mqtt():
    mqtt_client.loop_start()

@app.on_event("shutdown")
def stop_mqtt():
    mqtt_client.loop_stop()
    mqtt_client.disconnect()

@app.get("/")
def read_root():
    return {"message": "MQTT listener active"}