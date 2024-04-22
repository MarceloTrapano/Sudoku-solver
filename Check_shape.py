import cv2

vid = cv2.VideoCapture(0)

while True:
    ret, frame = vid.read()
    frame = cv2.resize(frame, (640, 640), fx = 0, fy = 0,
                         interpolation = cv2.INTER_CUBIC)
 
    # Display the resulting frame
    cv2.imshow('Frame', frame)
 
    key = cv2.waitKey(10)
    if 27 == key:
        break
 