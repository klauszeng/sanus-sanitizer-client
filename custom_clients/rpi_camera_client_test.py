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

# Initial GPIO Settings
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11,GPIO.IN)

#globals
NODE_ID = "A21"

log = []
pqueue = queue.PriorityQueue()
msgqueue = queue.PriorityQueue()


def fire_alert():
    print("Alert! Wash your hands!")

# again, placeholder/fake function to take place of the real API
def request_faces(job_id):
    # placeholder bullshit function - API will be here
    rand = random.randint(1,100)
    if(rand >= 1 and rand <= 1000):
        return "faces"
    elif(rand >= 1001 and rand <= 2000):
        return "all clear"
    elif(rand >= 2001 and rand <= 3000):
        return "timeout"
# peek at head of pqueue
def peek_timestamp_at_head():
    if(not pqueue.empty()):
        return pqueue.queue[0][0]
    else:
        return -1

# peek at head of msgqueue
def peek_timestamp_at_alert():
    if(not msgqueue.empty()):
        return msgqueue.queue[0][0]
    else:
        return -1

#placeholder function for generating job_id
def generate_job_id():
    print("generating job_id")
    job_id = random.randint(1,1000)
    return job_id

# placeholder function for sending photo and geting job_id
def capture_and_send(NODE_ID, img_buffer, img_size, timestamp):
    job_id = generate_job_id();
    return (job_id,timestamp)

def control_thread(): # always running on startup
    while(True):
        if(time.time() >= peek_timestamp_at_head() and not peek_timestamp_at_head() == -1):
            print("executing control thread")
            # dequeue and send job_id to server to request faces
            timestamp,job_id = pqueue.get()
            face_message = request_faces(job_id)
            if(face_message == "faces"):
                msgqueue.put((time.time(),job_id)) #current time
                print("placing in msgqueue")
            elif(face_message == "timeout"):
                # put the job back in the queue and try again
                pqueue.put((timestamp,job_id))

# thread that will only grab jobs from msgqueue
def alert_thread():
    while(True):
        
        if(not msgqueue.empty()):
            # dequeue head and then keep dequeuing until head is 1 second later than earliest timestamp        
            timestamp,job_id = msgqueue.get()
            while(peek_timestamp_at_alert() - timestamp < 1 and not peek_timestamp_at_alert() == -1):
                timestamp,job_id = msgqueue.get()
            fire_alert()        
                
                
                
        
        
# Start Major Threads
# this will be in the init fnction in the real file
control_thread = threading.Thread(name='control_thread', target=control_thread)
alert_thread = threading.Thread(name='alert_thread', target=alert_thread)
control_thread.daemon = True
alert_thread.daemon = True

control_thread.start()
alert_thread.start()


#Main loop for RPi    
while(True):
    
    if GPIO.input(11): # If the PIR sensor is giving a HIGH signal
        job_id,timestamp = capture_and_send(NODE_ID, 100, 100, time.time())
        pqueue.put((timestamp,job_id))
        print("added to queue")
        time.sleep(6)
    
    


