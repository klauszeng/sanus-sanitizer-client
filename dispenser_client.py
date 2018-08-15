import sys, os, time, json, threading, Queue, requests, io, base64, picamera, logging
import numpy as np 
import RPi.GPIO as GPIO
from helper_functions import proximity 

class DispenserClient:
    def __init__(self):
        '''
        Initialize all local variables and functions
        '''
        #
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('dispenser main loop logger')
        ## create a file handler
        handler = logging.FileHandler('dispenser_main.log')
        handler.setLevel(logging.INFO)
        ## create a logging format: time - name of logger - level - message
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
        handler.setFormatter(formatter)
        ## add the handlers to the logger
        self.logger.addHandler(handler)

        # camera 
        self.camera = picamera.PiCamera()
        self.camera.resolution = (1920, 1088) # 640x480,1296x730,640x1080, 1920x1088
        self.url = 'http://192.168.0.106:5000/sanushost/api/v1.0/sanitizer_img' ## Input
        self.node_id = 'D1'
        self.shape = '(1088, 1920, 3)' 
        self.image = np.empty((1088, 1920, 3), dtype=np.uint8)
        self.camera.start_preview(fullscreen=False, window = (100,20,640,480))
        self.logger.info('dispenser client camera initialized, start_preview executed')

        # distance sensor
        self.sensor = proximity.VL6180X(1)
        self.logger.info('dispenser client TOF sensor initialized')

        # GPIO - LED 
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18, GPIO.OUT)
        GPIO.setup(23, GPIO.OUT)
        self.logger.info('dispenser client GPIO check')

        # temporary data structure for storage
        self.payload_queue =  queue.Queue(10) # not sure what a good size is. Better have a dynamic queue
        self.local_file_queue = queue.Queue(10)
        self.logger.info('dispenser client message queue initialized')

        # post thread instantiate 
        self.post_thread = post_thread("post thread", self.payload_queue)
        self.post_thread.daemon = True 
        self.post_thread.start()
        self.logger.info('dispenser client message queue initialized')

    ''' Clean up later
    def capture_and_post(self):
        self.camera.capture(self.image, 'rgb')
        image_temp = self.image.astype(np.float64)
        image_64 = base64.b64encode(image_temp).decode('ascii')
        payload = {'NodeID': self.node_id, 'Timestamp': time.time(), 'Image': image_64, 'Shape': self.shape}
        headers = {'Content_Type': 'application/json', 'Accept': 'text/plain'}
        result = requests.post(self.url, json=payload, headers=headers)
        return result
        '''

    def capture(self):
        self.camera.capture(self.image, 'rgb')
        image_temp = self.image.astype(np.float64)
        image_64 = base64.b64encode(image_temp).decode('ascii')
        payload = {'NodeID': self.node_id, 'Timestamp': time.time(), 'Image': image_64, 'Shape': self.shape}
        headers = {'Content_Type': 'application/json', 'Accept': 'text/plain'}
        self.payload_queue.put(payload, headers)
        self.logger.debug('payload: %s, headers: %s', str(payload), str(headers))

    def read_distance(self):
        return self.sensor.read_distance() #return an int

class dispenser_thread(threading.Thread):
    def __init__(self, name, queue):
        # Logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('dispenser sub-loop logger')
        ## create a file handler
        handler = logging.FileHandler('dispenser_thead.log')
        handler.setLevel(logging.INFO)
        ## create a logging format: time - name of logger - level - message
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
        handler.setFormatter(formatter)
        ## add the handlers to the logger
        self.logger.addHandler(handler)

        # Initialize thread
        threading.Thread.__init__(self)
        self.name = name
        self.payload_queue = queue.Queue(10)
        self.storage_queue = queue.Queue(10)

    def run(self):
        while 1:
            if self.payload_queue.qsize():
                payload, headers = self.payload_queue.get()
                respond = requests.post(self.url, json=payload, headers=headers)
                if respond == 'timeout': #HTTP protocol return message looks different, change this
                    self.storage_queue.put(payload, headers)
                    self.logger.debug('payload moved from payload queue to storage due to %s', respond)
                elif respond == 'overload':
                    self.storage_queue.put(payload, headers)
                    self.logger.debug('payload moved from payload queue to storage due to %s', respond)
                elif respond == 'noface':
                    self.logger.debug('exit loop due to %s', respond)
                    pass
                elif respond == 'face':
                    self.logger.debug('exit loop due to %s', respond)
                    pass
            elif self.storage_queue.qsize():
                # check if more urgent information exists
                payload, headers = self.storage_queue.get()
                respond = requests.post(self.url, json=payload, headers=headers)
                if respond == 'timeout': #HTTP protocol return message looks different, change this
                    self.storage_queue.put(payload, headers)
                    self.logger.debug('try again later due to %s', respond)
                elif respond == 'overload':
                    self.storage_queue.put(payload, headers)
                    self.logger.debug('try again later  due to %s', respond)
                elif respond == 'noface':
                    self.logger.debug('exit loop due to %s', respond)
                    pass
                elif respond == 'face':
                    self.logger.debug('exit loop due to %s', respond)
                    pass

if __name__ == "__main__":
    logging.basicConfig(filename='debug.log', level=logging.INFO)
    logger = logging.getLogger('main dispenser logger')
    ## create a file handler
    handler = logging.FileHandler('dispenser_main.log')
    handler.setLevel(logging.INFO)
    ## create a logging format: time - name of logger - level - message
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
    handler.setFormatter(formatter)
    ## add the handlers to the logger
    logger.addHandler(handler)

    # Initialization
    client = DispenserClient()
    logger.info('dispenser client initialized')

    #Main loop
	while 1:
        distance = client.read_distance()  ## sensor sometimes takes 2 loop cycle to get back to normal reading
        logger.debug('distance: %d mm', distance)
        if distance >= 100:
            GPIO.output(18, True)
            time.sleep(0.5)
            GPIO.output(18, False)
        elif distance >= 20:
            GPIO.output(23, True)
            time.sleep(0.5)
            GPIO.output(23, False)
            cur_time = time.time()
            respond = client.capture_and_post()
            logger.info('capture successfully, respond returns in: %f s', time.time() - cur_time)
        else:
            sys.exit()
    sys.exit()
