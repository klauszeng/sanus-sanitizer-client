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

# Audio Alert imports
##from pydub import AudioSegment
##from pydub.playback import play

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
        time.sleep(2)
        
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
        
        # Load in all the audio first
        self.LUKA_A = 'aplay -q lukaAlert.wav'
        self.LUKA_W = 'aplay -q lukaWelcome.wav'
        self.KLAUS_A = 'aplay -q klausAlert.wav'
        self.KLAUS_W = 'aplay -q klausWelcome.wav'
        
        
    def send_alert(self,message):
        
        if(message == "LUKA_A"):
            os.system(self.LUKA_A)
        elif(message == "LUKA_W"):
            os.system(self.LUKA_W)
        elif(message == "KLAUS_W"):
            os.system(self.KLAUS_W)
        elif(message == "KLAUS_A"):
            os.system(self.KLAUS_A)
        
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
    def prepare_and_process(self, NODE_ID, timestamp, img_buffer, img_size):
        payload = {'NodeID': NODE_ID, 'Timestamp': timestamp, 'Image': img_buffer, 'Shape': img_size}
        headers = {'Content_Type': 'application/json', 'Accept': 'text/plain'}
        
        # the timestamp, payload, and header will be saved so that we can make another post request to determine HH status
        client.pqueue.put((timestamp, payload, headers))
        


    def control_thread(self): # always running on startup
        
        while(True):
            if(not self.pqueue.empty()):
                
                # dequeue and post request to get face statistics 
                timestamp, payload, headers = self.pqueue.get()
                print("sending post req")
                debug = time.time()
                result = requests.post(self.url, json=payload, headers=headers)
                print(result.json())
                if(result.json()['Status'][0] == True and result.json()['Status'][1] == 'luka'):
                    self.send_alert("LUKA_W")
                if(result.json()['Status'][0] == True and result.json()['Status'][1] == 'klaus'):
                    self.send_alert("KLAUS_W")
                
                # Determine status of person, if there is a staff member face and they are not on dispenser list
                self.msgqueue.put(((timestamp + 30), payload, headers))




##                if(face_message == "faces"):
##                    self.msgqueue.put((time.time(),job_id)) #current time
##                    print("placing in msgqueue")
##                elif(face_message == "timeout"):
##                    # put the job back in the queue and try again
##                    pqueue.put((timestamp,job_id))


    # thread that will only grab jobs from msgqueue
    def alert_thread(self):
        while(True):
            
            # check queue to see if it has passed 30 secs from current time
            if(self.peek_timestamp_at_alert() == -1):
                continue
            elif(self.peek_timestamp_at_alert() - time.time() <= 0.0):
                
                # dequeue head and then keep dequeuing until head is 1 second later than earliest timestamp
                # Now that 30 sec have past, we need to check and see if they have actually washed their hands in that timeframe
                timestamp, payload, headers = self.msgqueue.get()
                
                # send post request again and check result
                # if there is a face, and it is staff, and they are still not in the dispenser list, send an alert
                print("sending 2nd post req for alert")
                payload["Timestamp"] = time.time()
                result = requests.post(self.url, json=payload, headers=headers)
                print(result.json())
                # if result is staff and not in dispenser list
                # TODO: ADD VOICE LIBRARY FOR SOUND
##                if(result.json()['Status'] == True):
##                    self.send_alert("Please wash your hands!")
##                    alert = AudioSegment.from_wav("lukaWelcome.wav")
##                    play(alert)
##                if(result.json()['Status'] == False):
##                    self.send_alert("you are clean!")
                
                
                # FOR WHEN SERVER RETURNS STATUS AND NAME
                
                if(result.json()['Status'][0] == True and result.json()['Status'][1] == 'luka'):
                    self.send_alert("LUKA_A")
                elif(result.json()['Status'][0] == True and result.json()['Status'][1] == 'klaus'):
                    self.send_alert("KLAUS_A")
                elif(result.json()['Status'][0] == False):
                    self.send_alert("you are clean!")
      
      
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
        
        #print("sensor is off")
        
        if GPIO.input(11): # If the PIR sensor is giving a HIGH signal
            
            print("PIR triggered!!!!!")
            
            timestamp = time.time()
            
            # Take a picture, then send that picture to the HTTP thread
            img = np.empty((480, 640, 3), dtype=np.uint8)
            client.camera.capture(img, 'rgb')
            
            #print("taking a pic")
            
            image_temp = img.astype(np.float64)
            image_64 = base64.b64encode(image_temp).decode('ascii')
            
            client.prepare_and_process(client.NODE_ID, timestamp, image_64, client.shape)
            
            # sleep because of the sensor delay
            # clear the sensor
            
            time.sleep(2)
    
    


