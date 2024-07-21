# python 3.x

import logging
import random
import time
import json
import minimalmodbus
from paho.mqtt import client as mqtt_client
from gpiozero import CPUTemperature, LoadAverage, DiskUsage

BROKER = "192.168.131.114"
PORT = 1883
RPI_TOPIC = "/ecdls/rpi_sensors"
MODBUS_TOPIC = "/ecdls/modbus"
# generate client ID with pub prefix randomly
CLIENT_ID = "rpi"
USERNAME = "admin"
PASSWORD = "t5njce747"

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

FLAG_EXIT = False

# ---------------------- Modbus ----------------------

instrument = minimalmodbus.Instrument("/dev/ttyUSB0", 1)
instrument.serial.baudrate = 4800
instrument.serial.bytesize = 8
instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 0.05


def modbus_fetch_data(registers):
    modbus_json_data = {
        "temp": float("{:.3f}".format(registers[1] * 0.1)),
        "humid": float("{:.3f}".format(registers[0] * 0.1)),
    }

    return json.dumps(modbus_json_data)


# -----------------------------------------------------------


# -------------------------- RPI ----------------------------
def measure_cpu_temp():
    cpu = CPUTemperature()
    return float("{:.3f}".format(cpu.temperature))


def measure_cpu_load_avg():
    la = LoadAverage()
    return float("{:.3f}".format(la.load_average))


def measure_disk_usage():
    du = DiskUsage()
    return float("{:.3f}".format(du.value))


def rpi_fetch_data():
    rpi_json_data = {
        "cpu_temp": measure_cpu_temp(),
        "cpu_load_avg": measure_cpu_load_avg(),
        "disk_usage": measure_disk_usage(),
    }
    msg = json.dumps(rpi_json_data)
    return msg


# -----------------------------------------------------------


def on_connect(client, userdata, flags, rc):
    if rc == 0 and client.is_connected():
        print("Connected to MQTT Broker!")
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


def check_status(result, msg, topic):
    status = result[0]
    if status == 0:
        print(f"Published: `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")


def publish(client):
    while True:
        try:
            rpi_msg = rpi_fetch_data()
            rpi_result = client.publish(RPI_TOPIC, rpi_msg)
            check_status(rpi_result, rpi_msg, RPI_TOPIC)

            registers = instrument.read_registers(
                registeraddress=0, number_of_registers=3, functioncode=3
            )
            modbus_msg = modbus_fetch_data(registers)

            modbus_result = client.publish(MODBUS_TOPIC, modbus_msg)

            check_status(modbus_result, modbus_msg, MODBUS_TOPIC)
            time.sleep(1)
        except Exception as e:
            # print("Error:", e)
            pass


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
