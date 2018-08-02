import sys, os, time, json
import numpy as np 
import threading 
import Queue
#import requests, picamera, io, 


'''
Raspberry Pi client pbject for dispenser 
'''
class PiClient: 
    def __init__(self):
        self.camera = picamera.PiCamera()
        self.camera.resolution = (1920, 1088)
        self.camera.start_preview()
        time.sleep(2)
        self.url = 'http://192.168.1.169:5000/sanushost/api/v1.0/sanitizer_img' ## Input
        self.node_id = '1' ## Input
        self.shape = '(1088, 1920, 3)' 
        self.image = np.empty((1088, 1920, 3), dtype=np.uint8)
    def capture_and_post(self):
        timestamp = time.time()
        # stream = io.BytesIO()
        # self.camera.capture(stream, format='jpeg')
        # stream.seek(0)
        self.camera.capture(self.image, 'rgb')
        image_temp = self.image.astype(np.float64)
        image_64 = base64.b64encode(image_temp)
        # image_64 = base64.b64encode(stream.getvalue()).decode('ascii')
        payload = {'NodeID': self.node_id, 'Timestamp': timestamp, 'Image': image_64, 'Shape': self.shape}
        headers = {'Content_Type': 'application/json', 'Accept': 'text/plain'}
        result = requests.post(self.url, json=payload, headers=headers)
        print(result)
        return result

'''
This thread is for future use. We can also use this thread to control led light on demo day. 
'''
class alert_thread(threading.Thread):
	def __init__(self, name, queue):
		threading.Thread.__init__(self)
		self.name = name
		self.queue = queue
	def run(self): ## Loop for alert thread
		while 1:
			if not self.queue.empty():
				print self.queue.get()

if __name__ == "__main__":
	## Initialize local variables
	client = PiClient()
	## temporary data structure for storage
	work_queue =  Queue.Queue(10)
	local_file_queue = Queue.Queue(10)
	## alert thread instantiate 
	alert = alert_thread("alert", work_queue)
	alert.daemon = True 
	alert.start()


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
		# 	result = requests.post(self.url, json=payload, headers=headers)
		## code for try again, need to discuss this 


		## temporary testing code 
		work_queue.put((time.time(), "message:" + str(time.time())))
		time.sleep(2)
