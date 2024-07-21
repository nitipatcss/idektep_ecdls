import RPi.GPIO as GPIO
import time

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin where the LM35's output is connected
LM35_PIN = 17

# Function to read the temperature from the LM35 sensor
def read_lm35_temperature(pin):
    try:
        # Set up the GPIO pin as an input
        GPIO.setup(pin, GPIO.IN)

        # Wait for a brief moment for the sensor to stabilize
        time.sleep(0.1)

        # Read the analog value from the LM35 sensor
        adc_value = GPIO.input(pin)

        # Convert the ADC value to temperature in Celsius
        temperature_celsius = (adc_value / 1024.0) * 330.0 

        return temperature_celsius

    except:
        GPIO.cleanup()

if __name__ == "__main__":
    try:
        while True:
            temperature = read_lm35_temperature(LM35_PIN)
            print("Temperature: {:.3f}°C".format(temperature))
            time.sleep(2)  # Read temperature every 2 seconds

    except KeyboardInterrupt:
        GPIO.cleanup()

    finally:
        # Clean up GPIO settings at the end of the program
        GPIO.cleanup()