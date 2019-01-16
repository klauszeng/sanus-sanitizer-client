# Install Dependencies for dispenser node
Run '''pip install -r requirements.txt'''

# Issues/functions to address
1. Objects in queue reach maxium. Give up new or old data
2. Register as a new node 
3. Hardware self check/self diagnose 
4. Add a route to report error 

# config.ini convention
[PROPERTY]
Type: Dispenser
Unit: Surgical Intensive Care
Id: SanusOffice01

[SERVER]
Route: http://192.168.0.106:5000/sanushost/api/v1.0/sanitizer_img

[DEBUG]
LogLevel: Debug

[CAMERA]
Resolution: (640, 480)
Shape: (480, 640, 3)
Width: 480
Height: 640
Channel: 3
FullScreen: 0

# Example usage 
```
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
                #GPIO.output(23, True)
                #time.sleep(0.25)
                #GPIO.output(23, False)
                time.sleep(0.25)
            else:
                #GPIO.output(18, True)
                cur_time = time.time()
                respond = client.capture()
                logger.info('capture successfully, camera captured images returns in:' +
                    '%f s, now forwarding payload to http thread.', time.time() - cur_time)
                #GPIO.output(18, False)
                #os.system("aplay thanks.wav")
                time.sleep(2)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt")
            sys.exit()
```