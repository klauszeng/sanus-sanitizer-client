import picamera, requests, time, base64
import RPi.GPIO as GPIO
import numpy as np

class TestClient:
    def __init__(self, node_id, type='Dispenser', unit='Surgical Intensive Care'):
        # camera 
        self.camera = picamera.PiCamera()
        self.camera.resolution = (640, 480) # 640x480,1296x730,640x1080, 1920x1088
        self.url = 'http://192.168.0.103:5000/sanushost/api/v1.0/entry_img' ## Input
        self.node_id = node_id
        self.shape = '(480, 640, 3)' 
        self.image = np.empty((480, 640, 3), dtype=np.uint8)
        self.camera.start_preview(fullscreen=False, window = (100,20,0,0)) #100 20 640 480
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(4, GPIO.IN)
        print ('test client initialized')

    def capture(self):
        self.camera.capture(self.image, 'rgb')
        image_temp = self.image.astype(np.float64)
        image_64 = base64.b64encode(image_temp).decode('ascii')
        payload = {'NodeID': self.node_id, 'Timestamp': time.time() ,'Image': image_64, 'Shape': self.shape}
        headers = {'Content_Type': 'application/json', 'Accept': 'text/plain'}
        return requests.post(self.url, json=payload, headers=headers)

if __name__ == "__main__":
    client = TestClient('test_breach')
    while 1:
        try:
            if GPIO.input(4):
                time.sleep(0.25)
            else:
                cur_time = time.time()
                respond = client.capture()
                try:
                    print (respond.json()['StaffID'])
                except:
                    print (respond.json()['Status'])
                time.sleep(2)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt")
            sys.exit()
