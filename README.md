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

# Credits:  
* Caroline Dunn (https://github.com/carolinedunn/facial_recognition)
* Google API documentation