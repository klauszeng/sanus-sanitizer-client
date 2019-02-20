import threading, time, requests, base64, time
from PIL import Image
import numpy as np

class stress(threading.Thread):
    def __init__(self, name):
        # Initialize thread
        threading.Thread.__init__(self)
        self.name = name

        image = np.asarray(Image.open('luka.png'), dtype=np.uint8)
        shape_string = str(image.shape)
        image = image.astype(np.float64)
        img_64 = base64.b64encode(image).decode('ascii')
        self.url = 'http://192.168.0.101:5000/sanushost/api/v1.0/sanitizer_img'
        self.payload = {'NodeID': str(self.name), 'Timestamp': time.time() ,'Image': img_64, 'Shape': shape_string}
        self.headers = {'Content_Type': 'application/json', 'Accept': 'text/plain'}
        print(name + ': Initialized')

    def run(self):
        while 1:
            try:
                current = time.time()
                result = requests.post(self.url, json=self.payload, headers=self.headers)
                print('Thread ' + self.name + ': ' + str(time.time() - current))
            except:
                print('Thread ' + self.name + ': Something broke')
                continue
            
if __name__ == '__main__':
    thread_list = []
    for i in range(50):
        current = stress(str(i))
        current.daemon = True
        thread_list.append(current)
        current.start()

    while 1:
        pass
