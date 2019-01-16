import requests
import numpy as np
from PIL import Image
import base64
import ast
import time

url = 'http://192.168.0.103:5000/sanushost/api/v1.0/entry_img'
# url = 'http://localhost:5000/sanushost/api/v1.0/sanitizer_img'
# image = dlib.load_rgb_image('/home/billyzheng/Downloads/klaus2.jpg')

image = np.asarray(Image.open('rupert.png'), dtype=np.uint8)
# image = dlib.load_rgb_image('rupert.png')

shape_string = str(image.shape)
image = image.astype(np.float64)
# image_temp = np.reshape(image, (1, image.shape[0]*image.shape[1]*image.shape[2]))
img_64 = base64.b64encode(image).decode('ascii')
# payload = {"NodeID": "demo_sanitizer", "Timestamp": [time.time()], "Image": img_64, "Shape": shape_string}
payload = {"NodeID": "demo_entry", "Timestamp": time.time(), "Image": img_64, "Shape": shape_string}
headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
result = requests.post(url, json=payload, headers=headers)
print(result.json())
