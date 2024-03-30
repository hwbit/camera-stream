import cv2

def main():
    # RTSP URL of the sender's stream
    rtsp_url = 'rtsp://localhost:8080/stream'

    # Create a VideoCapture object
    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print("Error: Could not open RTSP stream.")
        return

    while True:
        ret, frame = cap.read()

        if ret:
            # Display the received frame
            cv2.imshow('frame', frame)

            # Exit if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    # Release the VideoCapture object
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
