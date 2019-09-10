import picamera
import cv2, base64
import numpy as np

class PiCamera:

    def __init__(self, 
        rotation = 0, 
        resolution = "640x480",
        image_size = (480, 640, 3),
        ):

        self.camera = picamera.PiCamera()
        self.camera.rotation = rotation 
        self.camera.resolution = resolution
        self.image = np.empty(image_size, dtype = np.uint8)
        self.camera.start_preview(fullscreen = False, window = (100,20,0,0))

    def capture(self, ):
        self.camera.capture(image, 'rgb')
        shape_string = str(image.shape)
        retval, buffer = cv2.imencode('.jpg', self.image)
        image_string = base64.b64encode(buffer)
        return image_string, shape_string
