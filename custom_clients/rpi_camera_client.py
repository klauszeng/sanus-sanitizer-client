"""
    AN IMPORTANT NOTE:
    This is just an outline code without API calls and filler functions. I just wrote this to get the general idea
    to see how things will work together
"""

import RPi.GPIO as GPIO
import time
import queue
import threading
import random
import sys, os, requests, time, json, picamera, io
from PIL import Image
import base64
import numpy as np

class PiClient:
    
    def __init__(self):
        # TODO: set location in environment variable
        # get location/deviceID from envvar and init with client type
        #self.ctype = os.environ['CLIENT_TYPE']
        self.CTENTRY = "ENTRY"
        #self.node_id = os.environ['LOCATION']
        self.NODE_ID = "demo_entry" #this will change once we place a random gen here
        
        # gpio pins initialization
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(11, GPIO.IN)

        # camera init
        self.camera = picamera.PiCamera()
        self.camera.resolution = (640, 480)
        self.camera.start_preview(fullscreen=False, window=(100, 20, 0, 0))
        
        # entry queues
        self.pqueue = queue.PriorityQueue()
        self.msgqueue = queue.PriorityQueue()
        
        # image place holder
        self.shape = '(480, 640, 3)'
        self.image = np.empty((480, 640, 3), dtype=np.uint8)
        
        # server info
        SERVER_HOST = '192.168.0.106'
        SERVER_PORT = '5000'
        # API url       THE SERVER HOST AND PORT WILL BE IN CONFIG FILE LATER
        self.url = 'http://' + SERVER_HOST + ':' + SERVER_PORT + '/sanushost/api/v1.0/entry_img'

        
    def fire_alert(self):
        print("Alert! Wash your hands!")

    # again, placeholder/fake function to take place of the real API
    def request_faces(self,job_id):
        # placeholder bullshit function - API will be here
        rand = random.randint(1,100)
        if(rand >= 1 and rand <= 1000):
            return "faces"
        elif(rand >= 1001 and rand <= 2000):
            return "all clear"
        elif(rand >= 2001 and rand <= 3000):
            return "timeout"
        
    # peek at head of pqueue
    def peek_timestamp_at_head(self):
        if(not self.pqueue.empty()):
            return self.pqueue.queue[0][0]
        else:
            return -1

    # peek at head of msgqueue
    def peek_timestamp_at_alert(self):
        if(not self.msgqueue.empty()):
            return self.msgqueue.queue[0][0]
        else:
            return -1

    #placeholder function for generating job_id
    def generate_job_id(self):
        print("generating job_id")
        job_id = random.randint(1,1000)
        return job_id

    # placeholder function for sending photo and getting a job_id
    def capture_and_send(self, NODE_ID, timestamp, img_buffer, img_size):
        payload = {'NodeID': NODE_ID, 'Timestamp': [timestamp], 'Image': img_buffer, 'Shape': img_size}
        headers = {'Content_Type': 'application/json', 'Accept': 'text/plain'}
        result = requests.post(self.url, json=payload, headers=headers)        
        
        print(result.json())
        
        job_id = self.generate_job_id()
        return (job_id,timestamp)

    def control_thread(self): # always running on startup
        while(True):
            if(time.time() >= self.peek_timestamp_at_head() and not self.peek_timestamp_at_head() == -1):
                print("executing control thread")
                # dequeue and send job_id to server to request faces
                timestamp,job_id = self.pqueue.get()
                face_message = self.request_faces(job_id)
                if(face_message == "faces"):
                    self.msgqueue.put((time.time(),job_id)) #current time
                    print("placing in msgqueue")
                elif(face_message == "timeout"):
                    # put the job back in the queue and try again
                    pqueue.put((timestamp,job_id))

    # thread that will only grab jobs from msgqueue
    def alert_thread(self):
        while(True):
            
            if(not self.msgqueue.empty()):
                # dequeue head and then keep dequeuing until head is 1 second later than earliest timestamp        
                timestamp,job_id = self.msgqueue.get()
                while(self.peek_timestamp_at_alert() - timestamp < 1 and not self.peek_timestamp_at_alert() == -1):
                    timestamp,job_id = msgqueue.get()
                self.fire_alert()
                
    # thread for posting and waiting for HTTP response
    def http_thread(self, NODE_ID, timestamp, img_buffer, img_size):
    	
        job_id,timestamp = client.capture_and_send(client.NODE_ID, timestamp, img_buffer, img_size)
        client.pqueue.put((timestamp,job_id))
                   
        
#### MAIN ####
if __name__ == '__main__':
    client = PiClient()
    
    # Start Major Threads
    control_thread = threading.Thread(name='control_thread', target=client.control_thread)
    alert_thread = threading.Thread(name='alert_thread', target=client.alert_thread)
    control_thread.daemon = True
    alert_thread.daemon = True

    control_thread.start()
    alert_thread.start()

    # Main loop for RPi    
    while(True):
        
        if GPIO.input(11): # If the PIR sensor is giving a HIGH signal
            
            print("PIR sensor")
            
            timestamp = time.time()
            
            # Take a picture, then send that picture to the HTTP thread
            img = np.empty((480, 640, 3), dtype=np.uint8)
            client.camera.capture(img, 'rgb')
            
            print("taking a pic")
            
            image_temp = img.astype(np.float64)
            image_64 = base64.b64encode(image_temp).decode('ascii')
            
            # send to HTTP thread
            http_thread = threading.Thread(kwargs={'NODE_ID': client.NODE_ID,'timestamp': timestamp, 'img_buffer': image_64, 'img_size': client.shape}, target=client.http_thread)
            http_thread.daemon = True
            http_thread.start()
            
            # sleep because of the sensor delay
            time.sleep(20)
    
    


