![PyPI](https://img.shields.io/pypi/pyversions/GPIO.svg?style=plastic)
# Sanus Solution Dispenser Client Project
### Prerequisites
- camera input
- sensor input
 
## Getting Started
Clone this project
```
git clone 
cd 
```
### Installing
Note: Packages in requirements may be outdated/depricated.
```
pip install -r requirements.txt
```

### Adafruit I2S 3W Stereo Audio Setup 
1. Running this should update /etc/asound.conf properly.
```sh
curl -sS https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/i2samp.sh | bash
```
2. check if desired sound card and device are set as default:
```sh
alsamixer 
aplay -l
```
3. Edit ~/.asoundrc and copy&paste the following
```sh
pcm.!default {
	type hw
	card 0
}

ctl.!default {
	type hw
	card 0 
}
```


## Running
``` 
python3 dispenser_client.py
```

## Issues/functions to address
1. If pi is not connected to the internet, manually update time by:
```sh
sudo date -s "utc time"
```

## Configuration
```sh
[PROPERTY]
Type: Dispenser
Unit: Surgical Intensive Care #example
Id: SanusOffice01 #example

[SERVER]
Route: [http://localhost:5000/sanushost/api/v1.0/sanitizer_img] ## Replace this with the server ip

[DEBUG]
LogLevel: Debug # Edit this to change logger behavior

[CAMERA]
Resolution: (640, 480)
Shape: (480, 640, 3)
Width: 480
Height: 640
Channel: 3
FullScreen: 0 
Rotation: 0 ## 0 if using pi camera, 180 if using Arducam
```

## Start on boot
### Creating a service
Create a .service file and copy the following. Edit fields needed.
```
[Unit]
Description=My service
After=network.target

[Service]
ExecStart=/usr/bin/python3 -u main.py
WorkingDirectory=/home/pi/myscript
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```	
In this instance, the service would run Python 3 from our working directory  /home/pi/myscript which contains our python program to run main.py.

Copy this file into /etc/systemd/system as root, for example:
```
sudo cp myscript.service /etc/systemd/system/myscript.service
```

Once this has been copied, you can attempt to start the service using the following command:
```
sudo systemctl start myscript.service
```
Stop it using following command:
```
sudo systemctl stop myscript.service
```
When you are happy that this starts and stops your app, you can have it start automatically on reboot by using this command:
```
sudo systemctl enable myscript.service
```

## Authors

Klaus

## License

 Copyright (c) <2019> <Sanus Solutions>

 Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.