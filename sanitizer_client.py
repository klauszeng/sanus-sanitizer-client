import configparser, logging
import queue, time, datetime, sys
import pi_camera, cv2, base64
import post_request_thread
import requests, json
import numpy as np
import RPi.GPIO as GPIO

try: 
        config = configparser.ConfigParser()
        config.read('config.ini')
except:
        raise Exception("config.ini file missing.")
        
class SanitizerClient:
    def __init__(self, ):

        ## post request thread instantiate 
        self.unit = config.get('PROPERTY', 'Unit')
        self.type = config.get('PROPERTY', 'Type')
        self.node_id = config.get('PROPERTY', 'Id')

        ## 
        self.route = config.get('SERVER', 'Route')
        self.init_logger()
        self.init_camera()
        self.init_ir_sensor()
        self.init_post_request_thread()

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
        #ch = logging.FileHandler('sanitizer_client.log')
        ch.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def init_camera(self, ):
        ## Retrive parameters from configuration file 
        resolution = config.get('CAMERA', 'Resolution')
        node_id = config.get('PROPERTY', 'Id')
        width = config.getint('CAMERA', 'Width')
        height = config.getint('CAMERA', 'Height')
        channel = config.getint('CAMERA', 'Channel')
        rotation = config.getint('CAMERA', 'Rotation')

        ## Camera
        self.camera = pi_camera.PiCamera(rotation, resolution, (width, height, channel))
        self.logger.info('sanitizer client camera initialized, start_preview executed')

    def init_ir_sensor(self, ):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(4, GPIO.IN) #motion sensor
        self.logger.info('sanitizer client GPIO check')

    def init_post_request_thread(self, ):
        ## message queue
        self.message_queue = queue.Queue()
        self.post_request_thread = post_request_thread.PostRequestThread(
            "PostRequest", self.node_id, self.type, self.unit, self.message_queue)
        self.post_request_thread.daemon = True 
        self.post_request_thread.start()
        self.logger.info('sanitizer client post request thread initialized')

    def capture(self):
        image_string, shape_string = self.camera.capture()
        payload = {'NodeID': self.node_id, 'Timestamp': time.time() ,'Image': image_string, 'Shape': shape_string}
        headers = {'Content_Type': 'application/json', 'Accept': 'text/plain'}
        self.message_queue.put((payload, headers, self.route)) # sanitizer thread

if __name__ == "__main__":

    # Initialization
    client = SanitizerClient()

    #Main loop
    while 1:
        try:
            if GPIO.input(4) == 0:
                time.sleep(0.5)
            else:
                respond = client.capture()
                time.sleep(2)
        except KeyboardInterrupt:
            sys.exit()
