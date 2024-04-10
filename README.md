# Camera-Stream
This project is for COMP 4300 (Winter 2024). 

It is built upon Caroline Dunn's facial recognition software. Instead of doing the processing locally, we will have a server stream a live stream from a webcam and have a client connect to the server and do some processing. The main intentions of this project is to record and compare networking metrics on different video streaming methods. It also looks at how the different streaming methods can affect local processing.

This project could have been done without the facial recognition portion but we wanted to implement an actual use case.

# How it works

Streams video from a device (Raspberry Pi) and allows a client to connect to the stream. The client side will do facial recognition from the incoming stream and perform a task based on the person. 

There are two implementations for the stream, one using HTTP and the other using Sockets. Upon facial recognition, the program will send an email based on the recognized face. Only the HTTP client has this implemented but it could easily be included in the socket implementation as well. This program is written such that is is not limited to just sending emails, it can be modified for other functionalities such as playing sounds, recording the video stream, or some sort of authentication.

# Required Equipment
* Client - your laptop/computer
* Raspberry Pi 4
* MicroSD card (32GB or better)
* Webcam

# Required Software and Packages - Needs installation on both PC and Raspberry Pi
* Python 3
* OpenCV, `pip install opencv-python` and `pip install opencv-contrib-python`
* imutil: `pip install imutil`
* face recognition: `pip install face-recognition` and `pip install face_recognition_models`
* Flask: `pip install Flask`

# Collecting Data on the Client
1. Create a folder `/dataset`
2. Create a folder in `/dataset` with name of a person. e.g., `/dataset/Henry`
3. Run file to take data to train with `python headshot.py`
   1. Take about 20 pictures of various angles and emotions
   2. (Take more pictures for better results)
4. Run file to train model: `python train_model.py`
   1. This would create an `encodings.pickle` file that contains the trained dataset
5. To test, run `python facial_req.py`

# Running the Server (Raspberry Pi)
1. Attach webcam to Raspberry Pi
2. Run file to start server
   1. `python http_server.py` or `python socket_server.py`
   2. Install any missing packages that may prevent program from running
   
# Connecting to Server
1. Update the URL in the same protocol you want with the IP address or hostname of the Raspberry Pi in `xxxx_client_face.py`
2. Run the file to connect to the server
   1. `python http_client_face.py` or `python socket_client_face.py`
   2. Install any missing packages that may prevent program from running
3. Press `q` to quit.

# Using the email feature
1. Create a Google Workspace account and create a project: https://developers.google.com/workspace/guides/create-project
2. Enable Google APIs: https://developers.google.com/workspace/guides/enable-apis
   1. Use scope: `https://mail.google.com/` 
3. Set up authentication for the account: https://developers.google.com/workspace/guides/create-credentials
   1. Create and download credentials.json
4. Create tokens: https://developers.google.com/docs/api/quickstart/python
   1. Run quickstart.py: `python quickstart.py`
   2. You will be prompt to log into Google to verify your application
5. Create a .env file with variable `EMAIL_ADDRESS`
   1. e.g., `EMAIL_ADDRESS="your-gmail-account-here"`
   2. Install dotenv library: `pip install python-dotenv`
6. Run `python http_server.py` on the Raspberry Pi
7. Run `python http_client_face_email.py` on the client

# Credits:  
* Caroline Dunn (https://github.com/carolinedunn/facial_recognition)
* Google API documentation
