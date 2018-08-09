import sys, os, time, json, threading, queue, requests, io, base64, picamera
import numpy as np 
import RPi.GPIO as GPIO
from helper_functions import proximity 

class DispenserClient:
	def __init__(self):
		'''
		Initialize all local variables and functions
		'''
		## camera 
		self.camera = picamera.PiCamera()
		self.camera.resolution = (1920, 1088) 
		self.url = 'http://192.168.0.103:5000/sanushost/api/v1.0/sanitizer_img' ## Input
		self.node_id = 'D1'
		self.shape = '(1088, 1920, 3)' 
		self.image = np.empty((1088, 1920, 3), dtype=np.uint8)
		print('dispenser client camera initialized')

		## distance sensor
		self.sensor = proximity.VL6180X(1)
		print('dispenser client TOF sensor initialized')

		## GPIO - LED 
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(18, GPIO.OUT)
		GPIO.setup(23, GPIO.OUT)
		print('dispenser client GPIO check')

		## temporary data structure for storage
		self.work_queue =  queue.Queue(10)
		self.local_file_queue = queue.Queue(10)
		print('dispenser client message queue initialized')

		## alert thread instantiate 
		self.alert = alert_thread("alert", self.work_queue)
		self.alert.daemon = True 
		self.alert.start()
		print('dispenser client alert thread initialized')

	def capture_and_post(self):
		self.camera.start_preview(fullscreen=False, window = (100,20,640,480))
		time.sleep(2)
		self.camera.capture(self.image, 'rgb')
		self.camera.stop_preview()
		image_temp = self.image.astype(np.float64)
		image_64 = base64.b64encode(image_temp)
		payload = {'NodeID': self.node_id, 'Timestamp': time.time(), 'Image': image_64, 'Shape': self.shape}
		headers = {'Content_Type': 'application/json', 'Accept': 'text/plain'}
		result = requests.post(self.url, json=payload, headers=headers)
		print(result)
		return result

	def read_distance(self):
		return self.sensor.read_distance() #return an int
		
class alert_thread(threading.Thread):
	def __init__(self, name, queue):
		threading.Thread.__init__(self)
		self.name = name
		self.queue = queue
	def run(self): ## Loop for alert thread
		while 1:
			if not self.queue.empty():
				print(self.queue.get())

if __name__ == "__main__":
	#logging.basicConfig(filename='debug.log', level=logging.DEBUG)		
		
	client = DispenserClient()
	print('dispenser client initialized successfully')
	
	#Main loop
	while 1:
		distance = client.read_distance()  ## sensor sometimes takes 2 loop cycle to get back to normal reading
		print(distance)
		if distance >= 100:
			GPIO.output(18, True)
			time.sleep(0.5)
			GPIO.output(18, False)
		elif distance >= 20:
			GPIO.output(23, True)
			time.sleep(0.5)
			GPIO.output(23, False)
			client.capture_and_post()
			print ('capture successfully')
		else:
			sys.exit()
			
	sys.exit()
