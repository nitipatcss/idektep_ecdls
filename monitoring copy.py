# python 3.x

import logging
import random
import time
import json
from paho.mqtt import client as mqtt_client
from gpiozero import CPUTemperature, LoadAverage, DiskUsage

BROKER = "192.168.131.114"
PORT = 1883
TOPIC = "/ecdls/sensors"
# generate client ID with pub prefix randomly
CLIENT_ID = "rpi"
USERNAME = "admin"
PASSWORD = "t5njce747"

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

FLAG_EXIT = False


def measure_cpu_temp():
    cpu = CPUTemperature()
    return float("{:.3f}".format(cpu.temperature))


def measure_cpu_load_avg():
    la = LoadAverage()
    return float("{:.3f}".format(la.load_average))


def measure_disk_usage():
    du = DiskUsage()
    return float("{:.3f}".format(du.value))


def fetch_data():
    json_data = {
        "cpu_temp": measure_cpu_temp(),
        "cpu_load_avg": measure_cpu_load_avg(),
        "disk_usage": measure_disk_usage(),
    }
    msg = json.dumps(json_data)
    return msg




def on_connect(client, userdata, flags, rc):
    if rc == 0 and client.is_connected():
        print("Connected to MQTT Broker!")
        # client.subscribe(TOPIC)
    else:
        print(f"Failed to connect, return code {rc}")


def on_disconnect(client, userdata, rc):
    logging.info("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        logging.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            logging.info("Reconnected successfully!")
            return
        except Exception as err:
            logging.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)
    global FLAG_EXIT
    FLAG_EXIT = True


def on_message(client, userdata, msg):
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")


def connect_mqtt():
    client = mqtt_client.Client(CLIENT_ID)
    # client.tls_set(ca_certs="./broker.emqx.io-ca.crt")
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, keepalive=120)
    client.on_disconnect = on_disconnect
    return client


def publish(client):
    while True:
        msg = fetch_data()
        result = client.publish(TOPIC, msg)
        status = result[0]
        if status == 0:
            print(f"Published: `{msg}` to topic `{TOPIC}`")
        else:
            print(f"Failed to send message to topic {TOPIC}")
        time.sleep(1)


def run():
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s: %(message)s", level=logging.DEBUG
    )
    client = connect_mqtt()
    client.loop_start()
    publish(client)
    # client.loop_forever()


if __name__ == "__main__":
    run()
