# Install Dependencies for local server 
**PLEASE USE VIRTUALENV**  
In a virtual env:  
1. In the ```sanus_face_server``` root directory, run ```pip install -r requirements.txt ```  

# Install Docker
1. Install docker, follow instruction for the OS where tensorflow serving model server will run (macos or linux).  

# Build the Docker image and run your container
1. There are 2 Dockerfiles. [Dockerfile](https://github.com/sanus-solutions/sanus-face-server/blob/master/Dockerfile) builds the minimal tensorflow serving container without GPU support, and [Dockerfile.devel](https://github.com/sanus-solutions/sanus-face-server/blob/master/Dockerfile.devel)(**Still in development**) builds the tensorflow serving container with GPU support. Note that the GPU support build uses bazel and will eat up all your RAM.  
2. Build the container with: ```docker build --pull -t <your_image_name_here> .```  
    or ```docker build --pull -t <your_image_name_here> -f Dockerfile.devel-gpu .``` 
3. Now run a container with: ```docker run --name <your_container_name_here> -it <your_image_name_here> bash```  
    and this will start an interactive bash shell in the container. Now you can run the model server with the following:  
    ```tensorflow_model_server --port=8500 --model_name=saved_model --model_base_path=/models``` Now the model server should be running in your Docker container. Note that you might have to ```cd ..``` once you're in the container bash. Just make sure you're in a directory that there's a ```\models``` directory.
    
# Run the local server
In the virtual env that you installed all the dependencies:  
1. In the repo root: ```export FLASK_APP=app.py```
2. Run ```flask run --host=0.0.0.0```
3. You might have to do: ```iptables -I INPUT -p tcp --dport 5000 -j ACCEPT``` to allow port 5000 traffic for Flask.  

# Sending requests to the local server
1. Check the local server's ip address in the router configuration page, and use that address in your request url.  
2. Flask runs on port 5000 by default.  