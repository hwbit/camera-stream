import cv2
import socket
import pickle
import struct

# Replace with server's IP
# URL = "10.0.0.98"
URL = "127.0.0.1" # local host

# Create a socket client
class Client():
    total_packets_received = 0
    
    def __init__(self, url):
        self.video_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.video_client_socket.connect((url, 9999))
        self.received_data = b""
        self.payload_size = struct.calcsize("<L")

    def run(self):
        print("Loading Video")

        while True:
            # Receive and assemble the data until the payload size is reached
            while len(self.received_data) < self.payload_size:
                self.received_data += self.video_client_socket.recv(4096)

            # Extract the packed message size
            packed_msg_size = self.received_data[:self.payload_size]
            self.received_data = self.received_data[self.payload_size:]
            msg_size = struct.unpack("<L", packed_msg_size)[0]

            # Receive and assemble the frame data until the complete frame is received
            while len(self.received_data) < msg_size:
                self.received_data += self.video_client_socket.recv(4096)

            # Extract the frame data
            frame_data = self.received_data[:msg_size]
            self.received_data = self.received_data[msg_size:]

            # Deserialize the received frame
            received_frame = pickle.loads(frame_data) 

            # Display the received frame
            cv2.imshow('Client Video', received_frame)

            # Press ‘q’ to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
        self.video_client_socket.close()
# end client
      
if __name__ == "__main__":
    c = Client(URL)
    c.run()