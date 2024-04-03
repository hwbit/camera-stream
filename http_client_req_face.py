import cv2
import requests
import numpy as np
from imutils.video import FPS
import face_recognition
import pickle
import cv2

url = "http://10.0.0.98:9999/"  # URL of the server streaming the video

broken = False

chunk_size = 16384

#Determine faces from encodings.pickle file model created from train_model.py
encodingsP = "encodings.pickle"
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(encodingsP, "rb").read())

def watch_stream():
    fps = FPS().start()
    currentname = "unknown"
    while True:        
        try:
            # get http response
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                bytes_data = bytes()
                # adjust rate limit
                for chunk in response.iter_content(chunk_size=chunk_size):
                    bytes_data += chunk
                    a = bytes_data.find(b'\xff\xd8')
                    b = bytes_data.find(b'\xff\xd9')
                    
                    # ensures there is data streaming
                    if a != -1 and b != -1:
                        jpg = bytes_data[a:b+2]
                        bytes_data = bytes_data[b+2:]
                        
                        # decode the data
                        frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                        
                        ## this handles the face recognition
                        boxes = face_recognition.face_locations(frame)
                        # compute the facial embeddings for each face bounding box
                        encodings = face_recognition.face_encodings(frame, boxes)
                        names = []

                        # loop over the facial embeddings
                        for encoding in encodings:
                            # attempt to match each face in the input image to our known
                            # encodings
                            matches = face_recognition.compare_faces(data["encodings"],
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
                                if currentname != name:
                                    currentname = name
                                    print(currentname)

                            # update the list of names
                            names.append(name)

                        # loop over the recognized faces
                        for ((top, right, bottom, left), name) in zip(boxes, names):
                            # draw the predicted face name on the image - color is in BGR
                            cv2.rectangle(frame, (left, top), (right, bottom),
                                (0, 255, 225), 2)
                            y = top - 15 if top - 15 > 15 else top + 15
                            cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                                .8, (0, 255, 255), 2)
                        
                        # show video
                        cv2.imshow('Stream', frame)
                        
                        # q to quit
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            broken = True
                            break
                        
                if broken:
                    break
                
                fps.update()
            else:
                print("Error receiving data from server")
                break
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    watch_stream()
