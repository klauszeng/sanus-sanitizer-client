import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)

while True:
	GPIO.output(18, True)
	GPIO.output(23, True)
	time.sleep(1)
	GPIO.output(18, False)
	GPIO.output(23, False)
	time.sleep(1)
