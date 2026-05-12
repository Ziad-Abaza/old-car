# Import libraries
from ultralytics import YOLO
import cv2 as c
import cvzone
import math
import time

cam = c.VideoCapture(0)  
# cam = c.VideoCapture("video/traffic1.mp4") 
cam.set(3, 1080)
cam.set(4, 720)

model = YOLO("best20.pt")

classNames = [
            "stop"
            ]
# Initialize time 
# prev_frame_time = 0
# new_frame_time = 0

while True:
    new_frame_time = time.time()
    success, img = cam.read()
    
    # Resize input image to match YOLO model's expected dimensions
    img = c.resize(img, (800, 800), interpolation=c.INTER_AREA)

    # Use YOLO model to detect objects
    results = model(img, stream=True)
    
    # rectangles , display text, calculate FPS
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            # c.rectangle(img,(x1,y1),(x2,y2),(255,0,255),3)
            w, h = x2 - x1, y2 - y1
            
            #rectangles & display text
            cvzone.cornerRect(img, (x1, y1, w, h))
            conf = math.ceil((box.conf[0] * 100)) / 100
            indexClass = int(box.cls[0])
            cvzone.putTextRect(img, f'{classNames[indexClass]} {conf}', (max(0, x1), max(35, y1)), scale=1, thickness=1)

    c.imshow("Image", img)
    if c.waitKey(1)  & 0xFF == 32:
        break
