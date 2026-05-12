import cv2
import numpy as np
from picamera2 import Picamera2
import tflite_runtime.interpreter as tflite


# interpreter = tflite.Interpreter(model_path=args.model_file)
cam = Picamera2()
height = 480
width = 640
middle = (int(width / 2), int(height / 2))
cam.configure(cam.create_video_configuration(main={"format": 'RGB888', "size": (width, height)}))

classnames = []
classfile = 'files/thing.names'

with open(classfile, 'rt') as f:
    classnames = f.read().rstrip('\n').split('\n')
# print(classnames)
p = 'files/frozen_inference_graph.pb'
v = 'files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'

net = cv2.dnn_DetectionModel(p, v)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)


cam.start()

while True:
    frame = cam.capture_array()
    # test = cv2.resize(frame, (0, 0), fx=1.5, fy=1.5)
    # classIds, confs, bbox = net.detect(test, confThreshold=0.5)

    # if len(classIds) > 0:
    #     for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
    #         cv2.rectangle(test, box, color=(0, 255, 0), thickness=3)
    #         cv2.putText(test, classnames[classId - 1],
    #                     (box[0] + 10, box[1] + 20),
    #                     cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), thickness=2)

    cv2.imshow("test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
