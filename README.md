Required Equipment
* Client - your laptop/computer
* Raspberry Pi 3
* Webcam

Required Software and Packages - Needs installation on both PC and Raspberry Pi
* Python 3
* OpenCV
* imutil

Collecting Data on the Client
1. Create a folder `/dataset`
2. Create a folder in `/dataset` with name of a person. e.g., `/dataset/Henry`
3. Run file to take data to train with `python headshot.py`
   1. Take roughly 10 pictures of various angles and emotions
4. Run file to train model: `python train_model.py`

Running the Server (Raspberry Pi)
1. Attach webcam to Raspberry Pi
2. Run file to start server
   1. `python http_server.py` or `python socket_server.py`

Connecting to Server

