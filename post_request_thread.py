import threading
import logging, configparser
import queue, time 
import requests, json, base64

class PostRequestThread(threading.Thread):
    def __init__(self, name, node_id, type, unit, queue):
        ###########################################################################################
        # Logger
        level = logging.DEBUG ## Temporary 
        self.logger = logging.getLogger('PostRequest')   
        self.logger.setLevel(level)
        ch = logging.FileHandler('log/connection.log')
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
        self.message_queue = queue

    def run(self):
        while 1:
            if self.message_queue.qsize():
                payload, headers, route = self.message_queue.get()
                self.logger.info("Payload unpacked.")
                try:
                    result = requests.post(route, json=payload, headers=headers)
                    code = result.status_code
                    if code != 200:
                        self.logger.debug(code)
                        with open('backup/' + str(payload['Timestamp']) + '.txt', 'wb') as f:
                            f.write(payload['Image'])
                except Exception as e:
                    self.logger.error("Unexpected error: " + str(e))
                    with open('backup/' + str(payload['Timestamp']) + '.txt', 'wb') as f:
                        f.write(payload['Image'])

if __name__ == "__main__":
    message_queue = queue.Queue()
    pt = PostRequestThread('test', 'test', 'test', 'test', message_queue)
    pt.daemon = True 
    pt.start()
    url = 'http://192.168.1.101:5000/sanushost/api/v1.0/identify_face'
    headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
    payload = {"NodeID": "demo_entry", "Timestamp": time.time(), "Image": "None" , "Shape": "(480, 640, 3)"}
    print(message_queue.put((payload, headers, url)))
    time.sleep(2)
    print(message_queue.put((1,2,3)))
