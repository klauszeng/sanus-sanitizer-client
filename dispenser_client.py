import sys, os, time, json, threading, queue, requests, io, base64, picamera, logging, random, datetime
import numpy as np 
import RPi.GPIO as GPIO
from PIL import Image

'''
Basic Structure 
dispenser client(main loop)
    --> http thread (sub loop of dispenser client, timely http request )
        --> second http thread (sub loop of http thread, less urgent request)
'''

class DispenserClient:
    def __init__(self, node_id, type='Dispenser', unit='Surgical Intensive Care', 
            url='http://192.168.0.106:5000/sanushost/api/v1.0/sanitizer_img'):
        ###########################################################################################
        '''
        Initialize all local variables and functions
        '''
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('dispenser main loop logger')
        ## create a file handler
        handler = logging.FileHandler('dispenser_object.log')
        handler.setLevel(logging.INFO)
        ## create a logging format: time - name of logger - level - message
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
        handler.setFormatter(formatter)
        ## add the handlers to the logger
        self.logger.addHandler(handler)
        ###########################################################################################

        # camera 
        self.camera = picamera.PiCamera()
        self.camera.resolution = (640, 480) # 640x480,1296x730,640x1080, 1920x1088
        self.url = url ## Input
        self.node_id = node_id
        self.shape = '(480, 640, 3)' 
        self.image = np.empty((480, 640, 3), dtype=np.uint8)
        self.camera.start_preview(fullscreen=False, window = (100,20,0,0)) #100 20 640 480
        self.logger.debug('dispenser client camera initialized, start_preview executed')
        
        # GPIO - LED & Distance Sensor
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        # GPIO.setup(18, GPIO.OUT) #red
        # GPIO.setup(23, GPIO.OUT) #green
        GPIO.setup(4, GPIO.IN) #motion sensor
        self.logger.debug('dispenser client GPIO check')

        # temporary data structure for storage
        self.payload_queue =  queue.Queue() # If length no supply for queue, it's dynamics
        self.logger.debug('dispenser client payload queue initialized') 

        # http thread instantiate 
        self.http = http_thread("http thread", self.node_id, type, unit, self.payload_queue)
        self.http.daemon = True 
        self.http.start()
        self.logger.debug('dispenser client http thread initialized')

    def capture(self):
        self.camera.capture(self.image, 'rgb')
        image_temp = self.image.astype(np.float64)
        image_64 = base64.b64encode(image_temp).decode('ascii')
        payload = {'NodeID': self.node_id, 'Timestamp': time.time() ,'Image': image_64, 'Shape': self.shape}
        headers = {'Content_Type': 'application/json', 'Accept': 'text/plain'}
        self.payload_queue.put((payload, headers, self.url)) # dispenser thread
        self.logger.debug('payload: %s, headers: %s', str(payload), str(headers))

    def update_url(self, new_url):
        self.url = new_url

    def update_node_id(self, new_node_id):
        self.node_id = new_node_id

    def update_unit(self, new_unit):
        self.unit = new_unit

class http_thread(threading.Thread):
    def __init__(self, name, node_id, type, unit, payload_queue):
        ###########################################################################################
        # Logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('http')
        handler = logging.FileHandler('http_thead.log')
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        ###########################################################################################

        # Initialize thread
        threading.Thread.__init__(self)
        self.name = name
        self.node_id = node_id
        self.type = type
        self.unit = unit
        self.payload_queue = payload_queue
        self.storage_queue = queue.Queue()

        ## Druid
        self.druid_url = 'http://192.168.0.106:8200/v1/post/hospital'
        self.druid_headers = {'Content-Type' : 'application/json'}

        # second_http thread instantiate 
        self.second_http = second_http_thread("http thread", node_id, type, unit, self.storage_queue)
        self.second_http.daemon = True 
        self.second_http.start()
        self.logger.debug('dispenser client second http thread initialized')


    def run(self):
        while 1:
            if self.payload_queue.qsize():
                payload, headers, url = self.payload_queue.get()
                result = requests.post(url, json=payload, headers=headers)
                status = result.json()['Status']
                code = result.status_code

                ## Success, either face or no face detected
                if code == '200': 
                    ## Inject data to druid
                    self.logger.info(druid_injection().json())
                else: ## Failure, including no return, bad request, bad gateway, overload etc
                    self.storage_queue.put(payload, headers, url)
                    self.logger.debug('http_thread: Exit due to error: %s. Will try again in 5s', code)


    def druid_injection(self):
        payload = {'type': self.type, 'staffID': None,
                'nodeID': self.node_id, 'unit': self.unit,  
                'room_number': None, 'staff_title': None,
                'response_type': None, 'response_message': None,
                'time': datetime.utcnow().isoformat()#random_date() #datetime.utcnow().isoformat()
                }
        return requests.post(self.druid_url, json=payload, headers=self.druid_headers)

class second_http_thread(threading.Thread):
    def __init__(self, name, node_id, type, unit, payload_queue):
        ###########################################################################################
        # Logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('second_http')
        handler = logging.FileHandler('second_http.log')
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        ###########################################################################################

        # Initialize thread
        threading.Thread.__init__(self)
        self.name = name
        self.node_id = node_id
        self.type = type
        self.unit = unit
        self.storage_queue = storage_queue
 
        ## Druid
        self.druid_url = 'http://192.168.0.106:8200/v1/post/hospital'
        self.druid_headers = {'Content-Type' : 'application/json'}

    def run(self):
        while 1:
            if self.storage_queue.qsize(): 
                time.sleep(5) # wait for 5 seconds before second attempt 
                result = requests.post(url, json=payload, headers=headers)
                status = result.json()['Status']
                code = result.status_code

                if code == '200':
                    ## Inject data to druid
                    self.logger.info(druid_injection().json())
                else:
                    ## If more attempts are needed, put payload back to storage queue
                    self.logger.debug('second_http_thread: Exit due to error: %s.', code)


    def druid_injection(self):
        payload = {'type': self.type, 'staffID': None,
                'nodeID': self.node_id, 'unit': self.unit,  
                'room_number': None, 'staff_title': None,
                'response_type': None, 'response_message': None,
                'time': datetime.utcnow().isoformat()#random_date() #datetime.utcnow().isoformat()
                }
        return requests.post(self.druid_url, json=payload, headers=self.druid_headers)


if __name__ == "__main__":
    
    ###########################################################################################
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('main dispenser logger')
    handler = logging.FileHandler('main.log')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    ###########################################################################################

    # Initialization
    client = DispenserClient('demo_sanitizer')
    logger.info('dispenser client initialized')

    #Main loop
    while 1:
        try:
            if GPIO.input(4):
                # GPIO.output(23, True)
                # time.sleep(0.25)
                # GPIO.output(23, False)
                # time.sleep(0.25)
                pass
            else:
                # GPIO.output(18, True)
                cur_time = time.time()
                result = client.capture()
                logger.info('capture successfully, camera captured images returns in:' +
                    '%f s, now forwarding payload to http thread.', time.time() - cur_time)
                # GPIO.output(18, False)
                #os.system("aplay thanks.wav")
                time.sleep(2)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt")
            sys.exit()
