# Sanus Solution Dispenser Unit

A deployment script for dispenser unit

## Getting Started

Clone this project

```
git clone https://github.com/sanus-solutions/sanus_face_server.git
```

### Prerequisites(Current version)

- python3 
- camera (Arducam)
- motion sensor(GPIO)

### Installing
Note: Packages in requirements may be outdated/depricated.
```
pip install -r requirements.txt
```

## Running
If unit is NOT connected to internet, do:
```
sudo date -s "new_date_time_string"
```
Then:
``` 
python3 dispenser_client.py
```

## Issues/functions to address
1. Objects in queue reach maxium. Give up new or old data
2. Register as a new node 
3. Hardware self check/self diagnose 
4. Add a route to report error 

## config.ini convention
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
Rotation: 0

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