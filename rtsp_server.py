import cv2

def main():
    # Open webcam
    cap = cv2.VideoCapture(0)

    # Set video resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Define codec and create VideoWriter object for RTSP
    rtsp_url = 'rtsp://localhost:8080/stream'
    fourcc = cv2.VideoWriter_fourcc(*'H264')
    out = cv2.VideoWriter(rtsp_url, fourcc, 20.0, (640, 480))

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            # Write the frame to RTSP stream
            out.write(frame)

            # Display the frame
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    # Release everything when done
    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
