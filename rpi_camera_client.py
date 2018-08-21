"""
    Author: Luka Antolic-Soban
    
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
        
        
    def send_alert(self,message):
        #SEND VOICE ALERT
        print(message)
        
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

    # placeholder function for sending photo and getting a job_id
    def capture_and_process(self, NODE_ID, timestamp, img_buffer, img_size):
        payload = {'NodeID': NODE_ID, 'Timestamp': [timestamp], 'Image': img_buffer, 'Shape': img_size}
        headers = {'Content_Type': 'application/json', 'Accept': 'text/plain'}
        
        # the timestamp, payload, and header will be saved so that we can make another post request to determine HH status
        client.pqueue.put((timestamp, payload, headers))
        
        
##        result = requests.post(self.url, json=payload, headers=headers)        
##        
##        print(result.json())
##        
##        job_id = self.generate_job_id()
##        return (job_id,timestamp)

    def control_thread(self): # always running on startup
        while(True):
            if(time.time() >= self.peek_timestamp_at_head() and not self.peek_timestamp_at_head() == -1):
                print("executing control thread")
                
                # dequeue and post request to get face statistics 
                timestamp, payload, headers = self.pqueue.get()
                result = requests.post(self.url, json=payload, headers=headers)
                print(result.json())
                
                
                # Determine status of person, if there is a staff member face and they are not on dispenser list
                self.msgqueue.put(((time.time()+30),payload, headers))
                print("placing in msgqueue")
                
##                if(face_message == "faces"):
##                    self.msgqueue.put((time.time(),job_id)) #current time
##                    print("placing in msgqueue")
##                elif(face_message == "timeout"):
##                    # put the job back in the queue and try again
##                    pqueue.put((timestamp,job_id))


    # thread that will only grab jobs from msgqueue
    def alert_thread(self):
        while(True):
            
            if(not self.msgqueue.empty()):
                
                # dequeue head and then keep dequeuing until head is 1 second later than earliest timestamp
                # Now that 30 sec have past, we need to check and see if they have actually washed their hands in that timeframe
                timestamp, payload, headers = self.msgqueue.get()
                
                # send post request again and check result
                # if there is a face, and it is staff, and they are still not in the dispenser list, send an alert 
                result = requests.post(self.url, json=payload, headers=headers)
                print(result.json())
                
                # if result is staff and not in dispenser list
                # TODO: ADD VOICE LIBRARY FOR SOUND
                self.send_alert("wash yo self")
      

######################################################################################################################################################
    #combining control_thread and http_thread 
    '''
    within capture_and_post():
        
        payload = {'NodeID': NODE_ID, 'Timestamp': [timestamp], 'Image': img_buffer, 'Shape': img_size}
        headers = {'Content_Type': 'application/json', 'Accept': 'text/plain'}
        client.pqueue.put((payload, headers))

    def control_thread(self, NODE_ID, timestamp, img_buffer, img_size):

        while(True):
            if [client].pqueue.size() and time.time() >= self.peek_timestamp_at_head() and not self.peek_timestamp_at_head() == -1: 
                payload, headers = [client].pqueue.get()
                result = client.capture_and_send(client.NODE_ID, timestamp, img_buffer, img_size)
                if result == True: #
                    DO NOTHING
                elseif result == False:
                    msqueue.put((timestamp, message))

    def alert_thread():
        
        while(true):
            if self.msqueue.qsize():
                timestamp, message = msqueue.get() 
                if timestamp + 30 > time.time():
                    time.sleep(time.time() - timestamp + 30)
                TextToSpeech.speak(message)
                time.sleep(3)
                ## need to think about the duplicate message. For demoday, make sure there aren't multiple messages 
    '''

######################################################################################################################################################

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
            
            client.capture_and_process(client.NODE_ID, timestamp, image_64, client.shape)
            
            # sleep because of the sensor delay
            time.sleep(20)
    
    


