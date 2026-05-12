from ultralytics import YOLO
import cv2
import cvzone
import math
from picamera2 import Picamera2
import time

# import yolov8n_ncnn_model

# cap = cv2.VideoCapture(0)

picam2 = Picamera2()
picam2.preview_configuration.main.size=(360,240)
picam2.preview_configuration.main.format = "RGB888"
picam2.start()

# cap = cv2.VideoCapture(0)
# cap.set(3,640)
# cap.set(4, 720)

model=YOLO("./yolov8n_ncnn_model")




classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush"
              ]
# frame_count = 0
while True:
    img = picam2.capture_array()
    # success, img =cap.read()

    results= model(img, stream=True)
    # frame_count += 1
    # if frame_count % 10 == 0:  # Calculate FPS every 10 frames
    #     end_time = time.time()
    #     elapsed_time = end_time - start_time
    #     fps = frame_count / elapsed_time
    #     print(f"FPS: {fps:.2f}")
    #     start_time = time.time()
    #     frame_count = 0
    for r in results:
        boxes = r.boxes
        for box in boxes:

            #bounding box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            # print(x1,y1,x2,y2)


            w, h = x2-x1,y2-y1
            bbox = int(x1), int(y1), int(w), int(h)
            cvzone.cornerRect(img,(x1,y1,w,h))


            #confidence
            conf=math.ceil((box.conf[0]*100))/100


            #class name
            cls = int(box.cls[0])

            cvzone.putTextRect(img,f'{classNames[cls]} {conf}',(max(0,x1),max(35,y1)),scale=0.7,thickness=1)

    cv2.imshow("Image",img)
    cv2.waitKey(1)
picam2.stop()
cv2.destroyAllWindows()






