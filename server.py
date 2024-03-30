import cv2
import socket
import pickle
import struct

class Server():
    def __init__(self):
        print("Starting...")
        self.video_capture = cv2.VideoCapture(0)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', 9999))  
        self.server_socket.listen(10)

        self.client_socket, self.client_address = self.server_socket.accept()
        print(f"[*] Accepted connection from {self.client_address}")
        
    def run(self):
        while True:
            ret, frame = self.video_capture.read()
            # self.video_capture.set(3, 800)
            # self.video_capture.set(4, 600)
            
            serialized_frame = pickle.dumps(frame)
            message_size = struct.pack("L", len(serialized_frame))
            self.client_socket.sendall(message_size + serialized_frame)

            cv2.imshow('Server Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.video_capture.release()
        self.cv2.destroyAllWindows()
            
#end class


if __name__ == "__main__":
    s = Server()
    while True:
        try:
            s.run()
        except KeyboardInterrupt:
            print("closed... restarting server...")
