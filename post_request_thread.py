import threading
import logging, configparser
import Queue 
import json

class PostRequestThread(threading.Thread):
    def __init__(self, name, node_id, type, unit):
        ###########################################################################################
        # Logger
        level = self.log_level(config.get('DEBUG', 'LogLevel'))
        self.logger = logging.getLogger('')   
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
        self.message_queue = Queue.Queue()

        
    def log_level(self, level):
        if level == 'Info':
            return logging.INFO
        else:
            return logging.DEBUG

    def run(self):
        while 1:
            if self.message_queue.qsize():
                payload, headers, route = self.message_queue.get()
                try:
                    result = requests.post(route, json=payload, headers=headers)
                    code = result.status_code
                except Exception, e:
                    self.logger.error("Unexpected error: " + str(e))
                    with open('/unsend_requests.json', 'w') as f:
                        f.write(json.dumps(payload))

if __name__ == "__main__":
    pt = PostRequestThread('test', 'test', 'test', 'test')
    pt.daemon = True 
    pt.start()
    print(1)