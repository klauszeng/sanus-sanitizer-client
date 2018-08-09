import sys, os, time, json, threading, Queue, requests, picamera, io
import numpy as np 
import RPi.GPIO as GPI
from helper_functions import proximity 

class DispenserClient:
	def __init__(self):
		'''
		Initialize all local variables and functions
		'''
		## camera 
		self.camera = PiCamera.PiCamera()
		self.camera.resolutions = (1920, 1088)
		self.url = 'http://192.168.1.91:5000/sanushost/api/v1.0/sanitizer_img' ## Input
		self.node_id = 'D1'
		self.shape = '(1088, 1920, 3)' 
		self.image = np.empty((1088, 1920, 3), dtype=np.uint8)

		## distance sensor
		self.sensor = proximity.VL6180X(1)

		## GPIO - LED 
		self.GPIO.setwarnings(False)
		self.GPIO.setmode(GPIO.BCM)
		self.GPIO.setup(18, GPIO.OUT)
		self.GPIO.setup(23, GPIO.OUT)

		## temporary data structure for storage
		self.work_queue =  Queue.Queue(10)
		self.local_file_queue = Queue.Queue(10)

		## alert thread instantiate 
		self.alert = alert_thread("alert", work_queue)
		self.alert.daemon = True 
		self.alert.start()

	def capture_and_post():
		# stream = io.BytesIO()
		# camera.capture(stream, format='jpeg')
		# stream.seek(0)
		self.camera.capture(self.image, 'rgb')
		image_temp = self.image.astype(np.float64)
		image_64 = base64.b64encode(image_temp)
		# image_64 = base64.b64encode(stream.getvalue()).decode('ascii')
		payload = {'NodeID': self.node_id, 'Timestamp': time.time(), 'Image': image_64, 'Shape': self.shape}
		headers = {'Content_Type': 'application/json', 'Accept': 'text/plain'}
		result = requests.post(self.url, json=payload, headers=headers)
		print(result)
		return result

	def read_distance():
		distance = self.sensor.read_distance() #return an int
		if distance <= 100:
			self.GPIO.output(18, True)
			time.sleep(0.5)
			self.GPIO.output(18, False)
			#client.capture_and_post()
		else:
			self.GPIO.output(23, True)
			time.sleep(0.5)
			self.GPIO.output(23, False)
			
class alert_thread(threading.Thread):
	def __init__(self, name, queue):
		threading.Thread.__init__(self)
		name = name
		queue = queue
	def run(self): ## Loop for alert thread
		while 1:
			if not queue.empty():
				print queue.get()

if __name__ == "__main__":

	client = DispenserClient()

	while 1: 
		''' Code for motion sensors 
		if motion:
			print 'taking pic'
			result = client.capture_and_post ## need to wait until some sort of result
			case 1 2 3 
		'''
		##  This conditionals will be put into capture and post method inside PiClient later
		# if result == None:
		# 	local_file_queue.add(payload)
		# elif result == "over load":
		# 	local_file_queue.add(payload)
		# elif result == "No face":
		# 	continue
		# elif result == "Face detected":
		# 	continue 
		# elif result == "slow response time":
		# 	result = requests.post(url, json=payload, headers=headers)
		## code for try again, need to discuss this 

		## temporary testing code 
		#work_queue.put((time.time(), "message:" + str(time.time())))
		#time.sleep(2)
			
		
		
