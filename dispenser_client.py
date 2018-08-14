import sys, os, time, json, threading, Queue, requests, io, base64, picamera, logging
import numpy as np 
import RPi.GPIO as GPIO
from helper_functions import proximity 

class DispenserClient:
    def __init__(self):
        '''
        Initialize all local variables and functions
        '''
        ##
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('dispenser_logger')
        logger.info('logger initialized')

        ## camera 
        self.camera = picamera.PiCamera()
        self.camera.resolution = (1920, 1088) # 640x480,1296x730,640x1080, 1920x1088
        self.url = 'http://192.168.0.106:5000/sanushost/api/v1.0/sanitizer_img' ## Input
        self.node_id = 'D1'
        self.shape = '(1088, 1920, 3)' 
        self.image = np.empty((1088, 1920, 3), dtype=np.uint8)
        self.camera.start_preview(fullscreen=False, window = (100,20,640,480))
        #self.camera.stop_preview()
        logger.info('dispenser client camera initialized, start_preview executed')

        ## distance sensor
        self.sensor = proximity.VL6180X(1)
        logger.info('dispenser client TOF sensor initialized')

        ## GPIO - LED 
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18, GPIO.OUT)
        GPIO.setup(23, GPIO.OUT)
        logger.info('dispenser client GPIO check')

        ## temporary data structure for storage
        self.work_queue =  queue.Queue(10)
        self.local_file_queue = queue.Queue(10)
        logger.info('dispenser client message queue initialized')

        ## alert thread instantiate 
        self.alert = alert_thread("alert", self.work_queue)
        self.alert.daemon = True 
        self.alert.start()
        logger.info('dispenser client message queue initialized')

    def capture_and_post(self):
        self.camera.capture(self.image, 'rgb')
        image_temp = self.image.astype(np.float64)
        image_64 = base64.b64encode(image_temp).decode('ascii')
        payload = {'NodeID': self.node_id, 'Timestamp': time.time(), 'Image': image_64, 'Shape': self.shape}
        headers = {'Content_Type': 'application/json', 'Accept': 'text/plain'}
        result = requests.post(self.url, json=payload, headers=headers)
        return result

    def capture(self):
        self.camera.capture(self.image, 'rgb')
        image_temp = self.image.astype(np.float64)
        image_64 = base64.b64encode(image_temp).decode('ascii')
        payload = {'NodeID': self.node_id, 'Timestamp': time.time(), 'Image': image_64, 'Shape': self.shape}
        headers = {'Content_Type': 'application/json', 'Accept': 'text/plain'}
        return (payload, headers)

    def read_distance(self):
        return self.sensor.read_distance() #return an int

class dispenser_thread(threading.Thread):
    def __init__(self, name, queue):
        threading.Thread.__init__(self)
        self.name = name
        self.queue = queue
    def run(self): ## Loop for alert thread
        while 1:
            if not self.queue.empty():
                ## TODO

if __name__ == "__main__":
    logging.basicConfig(filename='debug.log', level=logging.INFO)
    logger = logging.getLogger('main_dispenser_logger')
    logger.info('logger initialized')

    ## Initialization
    client = DispenserClient()
    logger.info('dispenser client initialized')
    payload_queue = Queue.Queue()
    upload_thread = dispenser_thread('upload', payload_queue)

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
            # respond = client.capture_and_post()
            payload_queue.add(client.capture())
            logger.info('Current queue size: %d', payload_queue.qsize())
            # logger.info('capture successfully, respond returns in: %f s', time.time() - cur_time)
        else:
            sys.exit()
    sys.exit()
