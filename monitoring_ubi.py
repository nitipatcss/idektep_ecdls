
from gpiozero import CPUTemperature, LoadAverage, DiskUsage
import RPI.GPIO as GPIO
import paho.mqtt.client as mqtt
import requests
import random
import time
import json

API_ENDPOINT = "https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}"
API_KEY = "BBFF-5pLtiHHhxHvIruf4NSMPX6j4wyJQQV"

GPIO.setup(GPIO.BCM)
GPIO.re

def measure_cpu_temp():
	cpu = CPUTemperature()
	return "{:.3f}".format(cpu.temperature)
 
def measure_cpu_load_avg():
  la = LoadAverage()
  return "{:.3f}".format(la.load_average)
  
def measure_disk_usage():
  du = DiskUsage()
  return "{:.3f}".format(du.value)

def build_payload(API_ENDPOINT, API_KEY, DATA):
    #Headers with the API Key
    headers = {
        "X-Auth-Token": API_KEY,
        "Content-Type": "application/json"
    }

    # Replace {DEVICE_LABEL} with the actual device label
    device_label = "rpi_test"
    url = API_ENDPOINT.format(DEVICE_LABEL=device_label)

    # Send data to Ubidots
    response = requests.post(url, json=DATA, headers=headers)

    # Check the response
    if response.status_code in [201,200]:
        print("Data sent successfully!")
    else:
        print("Failed to send data. Status code:", response.status_code)
        print("Response content:", response.content)
        print(url)

def main():
    json_data = {
          "cpu_temp":measure_cpu_temp(),
          "cpu_load_avg":measure_cpu_load_avg(),
          "disk_usage":measure_disk_usage(),
        }
    payload = json.dumps(json_data)
    build_payload(API_ENDPOINT, API_KEY, json_data)
    print(payload)
        
if __name__ == '__main__':
    while (True):
        main()
        time.sleep(10)
