# Credits: Caroline Dunn (https://github.com/carolinedunn/facial_recognition)

import cv2
import face_recognition
import numpy as np
import pickle
import requests
import struct
import threading
import time

from datetime import datetime
from openpyxl import Workbook

URL = "http://10.0.0.98:9999/"  # URL of the server streaming the video


# determines frame rate
# 4096, 8192, 16382, 32768
CHUNK_SIZE = 16382 # default 4096

# #Determine faces from encodings.pickle file model created from train_model.py
encodingsP = "encodings.pickle"
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(encodingsP, "rb").read())

class Client():
    total_packets_received = 0
    total_frames_received = 0
    total_packets_expected = 0
    last_packet_time = time.time()
    fps_interval_frames = 0
    fps_interval_start_time = time.time()
    total_data_received = 0
    total_data_expected = 0
    last_throughput_calc_time = time.time()
    last_throughput_data_received = 0
    total_latency = 0
    names = []
    currentname = "unknown"
    
    def __init__(self, url, chuck_size, data, run_time, face_req):
        self.url = url
        self.chunk_size = chuck_size
        self.data = data
        self.run_time = run_time
        self.face_req = face_req
        self.received_data = b""
        self.payload_size = struct.calcsize("<L")
        self.frame = []
        self.broken = False
        self.recv_frame = False
        self.boxes = None
        self.thread_exit = False

        # Create a workbook and select the active worksheet
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.append(["Timestamp", "Duration", "FPS", "Running Throughput (MB/s)", "Average Packet Latency (s)", "Processing Time (s)"])
    # end init
        
    def watch_stream(self):
        print("Loading Video")

        if self.face_req:
            thread = threading.Thread(target=self.face_recognition, args=()).start()
        
        start_time = time.time()
        broken = False
        while True:
            try:
                # get http response
                response = requests.get(self.url, stream=True)
                if response.status_code == 200:
                    bytes_data = bytes()
                    # adjust rate limit
                    for chunk in response.iter_content(chunk_size=self.chunk_size):
                        current_time = time.time()
                        bytes_data += chunk
                        a = bytes_data.find(b'\xff\xd8')
                        b = bytes_data.find(b'\xff\xd9')
                        
                        # ensures there is data streaming
                        if a != -1 and b != -1:
                            jpg = bytes_data[a:b+2]
                            bytes_data = bytes_data[b+2:]
                            
                            # decode the data
                            frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                            
                            if not self.recv_frame:
                                self.frame = frame 
                                self.recv_frame = True

                            # do face boxes
                            if self.face_req and self.boxes:
                                for ((top, right, bottom, left), name) in zip(self.boxes, self.names):
                                    # draw the predicted face name on the image - color is in BGR
                                    cv2.rectangle(frame, (left, top), (right, bottom),
                                        (0, 255, 225), 2)
                                    y = top - 15 if top - 15 > 15 else top + 15
                                    cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                                        .8, (0, 255, 255), 2)
                            
                            # show video
                            cv2.imshow('Stream', frame)
                            
                            # start metrics
                            self.do_metrics(start_time, current_time, jpg)
                            
                            # q to quit - after run time length
                            if cv2.waitKey(1) & 0xFF == ord('q') or (self.run_time> -1 and time.time() - start_time > self.run_time):
                                broken = True
                                self.thread_exit = True
                                break
                            
                        # end if - data streaming
                    # end for loop - response chunk    
                    if broken:
                        break
                    
                # end if response code == 200
                else:
                    print("Error receiving data from server")
                    break
            except Exception as e:
                print(f"Error: {e}")
                break
        # end while True
            
        self.save_metrics(start_time)
        
        # Release resources
        cv2.destroyAllWindows()
        if self.face_req:
            thread.join()
    # end watch stream
        
    def face_recognition(self):
        # while True:
        while not self.thread_exit:
            if self.recv_frame:
                ## this handles the face recognition
                self.boxes = face_recognition.face_locations(self.frame)
                # compute the facial embeddings for each face bounding box
                encodings = face_recognition.face_encodings(self.frame, self.boxes)

                # loop over the facial embeddings
                for encoding in encodings:
                    # attempt to match each face in the input image to our known
                    # encodings
                    matches = face_recognition.compare_faces(self.data["encodings"],
                        encoding)
                    name = "Unknown" #if face is not recognized, then print Unknown

                    # check to see if we have found a match
                    if True in matches:
                        # find the indexes of all matched faces then initialize a
                        # dictionary to count the total number of times each face
                        # was matched
                        matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                        counts = {}

                        # loop over the matched indexes and maintain a count for
                        # each recognized face face
                        for i in matchedIdxs:
                            name = self.data["names"][i]
                            counts[name] = counts.get(name, 0) + 1

                        # determine the recognized face with the largest number
                        # of votes (note: in the event of an unlikely tie Python
                        # will select first entry in the dictionary)
                        name = max(counts, key=counts.get)

                        #If someone in your dataset is identified, print their name on the screen
                        # ensures that name isn't spammed on screen
                        if self.currentname != name:
                            self.currentname = name
                            print(self.currentname)
                            
                    # update the list of names
                    self.names.append(name)
                    
                self.recv_frame = False
    # end facial recognition

    def do_metrics(self, start_time, current_time, jpg):
        # current_time = time.time()
        packet_latency = current_time - self.last_packet_time
        self.total_latency += packet_latency
        self.last_packet_time = current_time

        self.total_packets_received += 1
        self.total_frames_received += 1
        msg_size = len(jpg)
        self.total_data_received += msg_size
        self.total_data_expected += self.payload_size + msg_size

        # Calculate FPS
        self.fps_interval_frames += 1
        if current_time - self.fps_interval_start_time >= 1.0:  # Update FPS every second
            fps = self.fps_interval_frames / (current_time - self.fps_interval_start_time)
            current_timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Format timestamp with milliseconds

            # Calculate running throughput
            duration = current_time - start_time
            running_throughput = (self.total_data_received - self.last_throughput_data_received) / (current_time - self.last_throughput_calc_time) / (1024 * 1024)  # MB/s
            self.last_throughput_data_received = self.total_data_received
            self.last_throughput_calc_time = current_time

            # Calculate average packet latency
            avg_latency = self.total_latency / self.total_packets_received if self.total_packets_received != 0 else 0

            self.ws.append([current_timestamp, duration, fps, running_throughput, avg_latency, packet_latency])
            print("Logged:", [current_timestamp, duration, fps, running_throughput, avg_latency, packet_latency])

            self.fps_interval_frames = 0
            self.fps_interval_start_time = current_time
    # end do metrics
    
    def save_metrics(self, start_time):
        current_time = time.time()
        duration = current_time - start_time
        running_throughput = (self.total_data_received - self.last_throughput_data_received) / (current_time - self.last_throughput_calc_time) / (1024 * 1024)  # MB/s

        # Calculate average packet latency
        avg_latency = self.total_latency / self.total_packets_received if self.total_packets_received != 0 else 0

        current_timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Format timestamp with milliseconds
        self.ws.append([current_timestamp, duration, None, running_throughput, avg_latency])
        print("Logged:", [current_timestamp, duration, None, running_throughput, avg_latency])

        # Save the workbook
        self.wb.save(f"http_metrics_{self.chunk_size}-face_req_{self.face_req}.xlsx")   
    # end save metrics
#end class  
        
if __name__ == "__main__":  
    c = Client(URL, CHUNK_SIZE, data, run_time=300, face_req=True)
    c.watch_stream()
