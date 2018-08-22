import sys, os, time, json, threading, queue, requests, io, base64, picamera, logging
import numpy as np 
import RPi.GPIO as GPIO
from PIL import Image

class DispenserClient:
    def __init__(self):
        '''
        Initialize all local variables and functions
        '''
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('dispenser main loop logger')
        ## create a file handler
        handler = logging.FileHandler('dispenser_object.log')
        handler.setLevel(logging.INFO)
        ## create a logging format: time - name of logger - level - message
        formatter = logging
            .Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
        handler.setFormatter(formatter)
        ## add the handlers to the logger
        self.logger.addHandler(handler)

        # camera 
        self.camera = picamera.PiCamera()
        self.camera.resolution = (640, 480) # 640x480,1296x730,640x1080, 1920x1088
        self.url = 'http://192.168.0.106:5000/sanushost/api/v1.0/sanitizer_img' ## Input
        self.node_id = 'demo_sanitizer'
        self.shape = '(480, 640, 3)' 
        self.image = np.empty((480, 640, 3), dtype=np.uint8)
        self.camera.start_preview(fullscreen=False, window = (0,0,0,0)) #100 20 640 480
        self.logger
            .debug('dispenser client camera initialized, start_preview executed')
        
        # GPIO - LED & Distance Sensor
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM) 
        GPIO.setup(18, GPIO.OUT) # pin for green LED   
        GPIO.setup(23, GPIO.OUT) # pin for red LED
        GPIO.setup(4, GPIO.IN) # pin for motion sensor
        self.logger.debug('dispenser client GPIO check')

        # temporary data structure for storage
        self.payload_queue =  queue.Queue() # If length no supply for queue, it's dynamics
        self.logger.debug('dispenser client payload queue initialized') 

        # post thread instantiate 
        self.post_thread = dispenser_thread("post thread", self.payload_queue)
        self.post_thread.daemon = True 
        self.post_thread.start()
        self.logger.debug('dispenser client post thread initialized')

    def capture(self):
        self.camera.capture(self.image, 'rgb')
        image_temp = self.image.astype(np.float64)
        image_64 = base64.b64encode(image_temp).decode('ascii')
        payload = {'NodeID': self.node_id, 'Timestamp': time.time()
            ,'Image': image_64, 'Shape': self.shape}
        headers = {'Content_Type': 'application/json', 'Accept': 'text/plain'}
        self.payload_queue.put((payload, headers, self.url)) # dispenser thread
            #get the payload on the other side
        self.logger.debug('payload: %s, headers: %s', str(payload), str(headers))

class dispenser_thread(threading.Thread):
    def __init__(self, name, payload_queue):
        # Logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('dispenser sub-loop logger')
        handler = logging.FileHandler('dispenser_thead.log')
        handler.setLevel(logging.INFO)
        formatter = logging
            .Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Initialize thread
        threading.Thread.__init__(self)
        self.name = name
        self.payload_queue = payload_queue
        self.storage_queue = queue.Queue()

    def run(self):
        while 1:
            ## demo day hard code
            if self.payload_queue.qsize():
                cur_time = time.time()
                payload, headers, url = self.payload_queue.get()
                respond = requests.post(url, json=payload, headers=headers)
                if respond:
                    self.logger.info('payload received by http thread,' +
                        'respond return from server in: %f s. Status: %s'
                        ,time.time() - cur_time, respond.json()["Status"]) # beaware respond type 
                else:
                    # TODO
                    # Code on raspberry pi
                    # Import Image 

            # Comment out for demo day
            # look into 
            ''' 
            # Redo if statements according to HTTP protocol responds
            if self.payload_queue.qsize():
                payload, headers, url = self.payload_queue.get()
                respond = requests.post(url, json=payload, headers=headers)
                if respond == 'timeout': #HTTP protocol return message looks different, change this
                    self.storage_queue.put(payload, headers)
                    self.logger.debug('payload moved from payload queue to storage due to %s', respond)
                elif respond == 'overload':
                    self.storage_queue.put(payload, headers)
                    self.logger.debug('payload moved from payload queue to storage due to %s', respond)
                elif respond == 'False':
                    self.logger.debug('exit loop due to %s', respond)
                    pass
                elif respond == 'True':
                    self.logger.debug('exit loop due to %s', respond)
                    pass
            elif self.storage_queue.qsize(): #a new thread for this? 
                # check if more urgent information exists
                payload, headers = self.storage_queue.get()
                respond = requests.post(self.url, json=payload, headers=headers)
                if respond == 'timeout': #HTTP protocol return message looks different, change this
                    self.storage_queue.put(payload, headers)
                    self.logger.debug('try again later due to %s', respond)
                elif respond == 'overload':
                    self.storage_queue.put(payload, headers)
                    self.logger.debug('try again later  due to %s', respond)
                elif respond == 'False':
                    self.logger.debug('exit loop due to %s', respond)
                    pass
                elif respond == 'True':
                    self.logger.debug('exit loop due to %s', respond)
                    pass'''

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('main dispenser logger')
    handler = logging.FileHandler('main.log')
    handler.setLevel(logging.INFO)
    formatter = logging
        .Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Initialization
    client = DispenserClient()
    logger.info('dispenser client initialized')

    ''#Main loop
    while 1:
        try:
            if GPIO.input(21):
                GPIO.output(18, True)
                time.sleep(0.25)
                GPIO.output(18, False)
                time.sleep(0.25)
            else:
                GPIO.output(23, True)
                cur_time = time.time()
                respond = client.capture()
                logger.info('capture successfully, camera captured images returns in:' +
                    '%f s, now forwarding payload to http thread.', time.time() - cur_time)
                GPIO.output(23, False)
        except KeyboardInterrupt:
            print ("KeyboardInterrupt")
            sys.exit()

