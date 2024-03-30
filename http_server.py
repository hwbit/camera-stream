import cv2
import pickle
import struct
from flask import Flask, Response

app = Flask(__name__)

class Server():
    def __init__(self):
        print("Starting...")
        # self.resolution = (1280, 720)
        self.resolution = (800, 600)

        self.video_capture = cv2.VideoCapture(0)
        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        
    def get_frame(self):
        while True:
            ret, frame = self.video_capture.read()
            # serialized_frame = pickle.dumps(frame)
            # message_size = struct.pack("L", len(serialized_frame))
            imgencode=cv2.imencode('.jpg',frame)[1]
            stringData=imgencode.tobytes()
            # yield (b'--frame\r\n'
            #        b'Content-Type: image/jpeg\r\n\r\n' + serialized_frame + b'\r\n')
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + stringData + b'\r\n')

@app.route('/')
def index():
    return Response(Server().get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9999, debug=True)
