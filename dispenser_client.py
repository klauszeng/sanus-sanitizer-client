import sys, time, json, threading, queue, requests, io, base64, picamera, logging, datetime, configparser
import numpy as np 
import RPi.GPIO as GPIO
from PIL import Image

try: 
        config = configparser.ConfigParser()
        config.read('config.ini')
except:
        raise Exception("config.ini file missing.")
        
class DispenserClient:
    def __init__(self, ):

        self.route = config.get('SERVER', 'Route')
        self.init_logger()
        self.init_camera()
        self.init_ir_sensor()

        # temporary data structure for storage
        self.payload_queue =  queue.Queue() # If length no supply for queue, it's dynamics
        self.logger.info('dispenser client payload queue initialized') 

        # http thread instantiate 
        unit = config.get('PROPERTY', 'Unit')
        self.http = http_thread("http thread", self.node_id, type, unit, self.payload_queue)
        self.http.daemon = True 
        self.http.start()
        self.logger.info('dispenser client http thread initialized')

    def init_logger(self, ):
        ## Retrive parameters from configuration file
        debug_level = config.get('DEBUG', 'LogLevel')
        property_type = config.get('PROPERTY', 'Type')

        ## Logger
        if debug_level == 'Info':
            level = logging.INFO
        else:
            level = logging.DEBUG

        self.logger = logging.getLogger(property_type)
        self.logger.setLevel(level)
        ch = logging.StreamHandler()
        #ch = logging.FileHandler('dispenser_client.log')
        ch.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def init_camera(self, ):
        ## Retrive parameters from configuration file 
        resolution = config.get('CAMERA', 'Resolution')
        node_id = config.get('PROPERTY', 'Id')
        shape = config.get('CAMERA', 'Shape')
        width = config.getint('CAMERA', 'Width')
        height = config.getint('CAMERA', 'Height')
        channel = config.getint('CAMERA', 'Channel')
        rotation = config.getint('CAMERA', 'Rotation')

        ## Camera
        self.camera = picamera.PiCamera()
        self.camera.rotation = rotation
        self.camera.resolution = resolution
        self.node_id = node_id
        self.shape = shape
        size = (width, height, channel)
        self.image = np.empty(size, dtype=np.uint8)
        self.camera.start_preview(fullscreen=False, window = (100,20,0,0))
        self.logger.info('dispenser client camera initialized, start_preview executed')

    def init_ir_sensor(self, ):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(4, GPIO.IN) #motion sensor
        self.logger.info('dispenser client GPIO check')

    def capture(self):
        self.camera.capture(self.image, 'rgb')
        image_temp = self.image.astype(np.float64)
        image_64 = base64.b64encode(image_temp).decode('ascii')
        payload = {'NodeID': self.node_id, 'Timestamp': time.time() ,'Image': image_64, 'Shape': self.shape}
        headers = {'Content_Type': 'application/json', 'Accept': 'text/plain'}
        self.payload_queue.put((payload, headers, self.route)) # dispenser thread

    def update_route(self, new_route):
        self.route = new_route

    def update_node_id(self, new_node_id):
        self.node_id = new_node_id

    def update_unit(self, new_unit):
        self.unit = new_unit

class http_thread(threading.Thread):
    def __init__(self, name, node_id, type, unit, payload_queue):
        ###########################################################################################
        # Logger
        level = self.log_level(config.get('DEBUG', 'LogLevel'))
        self.logger = logging.getLogger('http thread')
        self.logger.setLevel(level)
        ch = logging.StreamHandler()
        #ch = logging.FileHandler('dispenser_client.log')
        ch.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        ###########################################################################################

        # Initialize thread
        threading.Thread.__init__(self)
        self.name = name
        self.node_id = node_id
        self.type = type
        self.unit = unit
        self.payload_queue = payload_queue
        self.storage_queue = queue.Queue()

        # second_http thread instantiate 
        self.second_http = second_http_thread("http thread", node_id, type, unit, self.storage_queue)
        self.second_http.daemon = True 
        self.second_http.start()
        self.logger.info('dispenser client second http thread initialized')
        
    def log_level(self, level):
        if level == 'Info':
            return logging.INFO
        else:
            return logging.DEBUG

    def run(self):
        while 1:
            if self.payload_queue.qsize():
                payload, headers, route = self.payload_queue.get()
                try:
                    result = requests.post(route, json=payload, headers=headers)
                    code = result.status_code
                    self.logger.debug(result.json())
                    if code == 200:
                        self.logger.info('HTTP request received.')
                    else:
                        self.storage_queue.put((payload, headers, route))
                except:
                    self.logger.info("Failed to establish connection with server. Try again in 5s.")
                    self.storage_queue.put((payload, headers, route))

class second_http_thread(threading.Thread):
    def __init__(self, name, node_id, type, unit, storage_queue):
        ###########################################################################################
        # Logger
        level = self.log_level(config.get('DEBUG', 'LogLevel'))
        self.logger = logging.getLogger('second http thread')	
        self.logger.setLevel(level)
        ch = logging.FileHandler('dispenser_client.log')
        ch.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        ###########################################################################################

        # Initialize thread
        threading.Thread.__init__(self)
        self.name = name
        self.node_id = node_id
        self.type = type
        self.unit = unit
        self.storage_queue = storage_queue

    def log_level(self, level):
        if level == 'Info':
            return logging.INFO
        else:
            return logging.DEBUG
            
    def run(self):
        while 1:
            if self.storage_queue.qsize(): 
                time.sleep(5) # wait for 5 seconds before second attempt 
                payload, headers, route = self.storage_queue.get()
                try:
                    result = requests.post(route, json=payload, headers=headers) 
                    code = result.status_code
                    self.logger.debug(result.json())
                    if code == 200:
                        self.logger.info("second attempt successful.")
                    else:
                        self.logger.info("second attempt failed with code: " + str(code))
                        self.storage_queue.put((payload, headers, route))
                except:
                    self.storage_queue.put((payload, headers, route))
                    self.logger.info("Failed to establish connection with server again. Try again in 30s.")
                    time.sleep(25)

if __name__ == "__main__":

    # Initialization
    client = DispenserClient()

    #Main loop
    while 1:
        try:
            if GPIO.input(4):
                time.sleep(0.25)
            else:
                cur_time = time.time()
                respond = client.capture()
                time.sleep(2)
        except KeyboardInterrupt:
            sys.exit()
