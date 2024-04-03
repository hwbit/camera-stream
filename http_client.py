import cv2
import requests
import numpy as np

url = "http://10.0.0.98:9999/"  # URL of the server streaming the video

broken = False

def watch_stream():
    while True:
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                bytes_data = bytes()
                for chunk in response.iter_content(chunk_size=4096):
                    bytes_data += chunk
                    a = bytes_data.find(b'\xff\xd8')
                    b = bytes_data.find(b'\xff\xd9')
                    if a != -1 and b != -1:
                        jpg = bytes_data[a:b+2]
                        bytes_data = bytes_data[b+2:]
                        frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                        cv2.imshow('Stream', frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            broken = True
                            break
                if broken:
                    break
            else:
                print("Error receiving data from server")
                break
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    watch_stream()
