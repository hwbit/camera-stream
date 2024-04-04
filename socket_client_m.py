import cv2
import face_recognition
import pickle
import socket
import struct
import time
from datetime import datetime
from openpyxl import Workbook

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
    
    # default 4096
    # incrase this number for better fps
    recv_size = 4096
    
    def __init__(self):
        self.video_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.video_client_socket.connect(("10.0.0.102", 9999))  # Replace with the server’s IP address
        self.received_data = b""
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

            # Display the received frame
            cv2.imshow('Client Video', received_frame)

            # Press ‘q’ to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Calculate final running throughput
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

        # Release resources
        cv2.destroyAllWindows()
        self.video_client_socket.close()
        


if __name__ == "__main__":
    c = Client()
    c.run()
