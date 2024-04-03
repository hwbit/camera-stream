import cv2
import face_recognition
import numpy as np
import socket
import pickle
import struct
import time

from imutils.video import FPS
from datetime import datetime
from openpyxl import Workbook


# URL = "10.0.0.98"  # URL of the server streaming the video
URL = "127.0.0.1"

# determines frame rate
CHUNK_SIZE = 16384 # default 4096

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

    def __init__(self, url, data, recv_size):
        self.video_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.video_client_socket.connect((url, 9999))  # Replace with the server’s IP address
        self.received_data = b""
        self.data = data
        self.recv_size = recv_size
        self.payload_size = struct.calcsize("<L")

        # Create a workbook and select the active worksheet
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.append(["Timestamp", "Duration", "FPS", "Running Throughput (MB/s)", "Average Packet Latency (s)"])

    def run(self):
        print("Loading Video")

        start_time = time.time()

        while True:
            while len(self.received_data) < self.payload_size:
                self.received_data += self.video_client_socket.recv(self.recv_size)

            packed_msg_size = self.received_data[:self.payload_size]
            self.received_data = self.received_data[self.payload_size:]
            msg_size = struct.unpack("<L", packed_msg_size)[0]

            while len(self.received_data) < msg_size:
                self.received_data += self.video_client_socket.recv(self.recv_size)

            frame_data = self.received_data[:msg_size]
            self.received_data = self.received_data[msg_size:]

            received_frame = pickle.loads(frame_data)
            
            self.face_recognition(received_frame)
            
            # do metrics
            self.do_metrics(start_time, msg_size)

            # Display the received frame
            cv2.imshow('Client Video', received_frame)

            # Press ‘q’ to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Calculate final running throughput
        self.save_metrics(start_time)
        
        # Release resources
        cv2.destroyAllWindows()
        self.video_client_socket.close()

    # end watch stream
        
    def face_recognition(self, frame):
        ## this handles the face recognition
        boxes = face_recognition.face_locations(frame)
        # compute the facial embeddings for each face bounding box
        encodings = face_recognition.face_encodings(frame, boxes)

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
                    name = data["names"][i]
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

        # loop over the recognized faces
        for ((top, right, bottom, left), name) in zip(boxes, self.names):
            # draw the predicted face name on the image - color is in BGR
            cv2.rectangle(frame, (left, top), (right, bottom),
                (0, 255, 225), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                .8, (0, 255, 255), 2)
    # end facial recognition

    def do_metrics(self, start_time, msg_size):
            current_time = time.time()
            packet_latency = current_time - self.last_packet_time
            self.total_latency += packet_latency
            self.last_packet_time = current_time

            self.total_packets_received += 1
            self.total_frames_received += 1
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

                self.ws.append([current_timestamp, duration, fps, running_throughput, avg_latency])
                print("Logged:", [current_timestamp, duration, fps, running_throughput, avg_latency])

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
        self.wb.save("socket_metrics.xlsx")  
    # end save metrics       

if __name__ == "__main__":
    c = Client(URL, data, CHUNK_SIZE)
    c.run()