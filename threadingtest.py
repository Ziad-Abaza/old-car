import cv2
import WebcamModule as wM
import numpy as np
import tensorflow as tf
import threading
import motormodule as motor
import queue  # Import queue module for thread-safe communication

# Object Detection Setup
classnames = []
classfile = 'files/thing.names'

with open(classfile, 'rt') as f:
    classnames = f.read().rstrip('\n').split('\n')

p = 'files/frozen_inference_graph.pb'
v = 'files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'

net = cv2.dnn_DetectionModel(p, v)
net.setInputSize(320, 230)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

# TFLite Setup
steeringSen = 0.50
maxThrottle = 0.25
ThrottleSen = 0.65

interpreter = tf.lite.Interpreter(model_path='working.tflite')
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Motor Control
# motor = motor.Motor(2, 3, 4, 17, 22, 27)  # Pin Numbers

# Preprocess Function for TFLite
def preProcess(img):
    img = img[54:120, :, :]
    img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    img = cv2.resize(img, (200, 66))
    img = img / 255
    return img

# Shared image object to be updated in the object_detection thread
img_queue = queue.Queue(maxsize=1)  # Use a queue to pass image data safely between threads

# Object Detection Thread
def object_detection():
    while True:
        frame = wM.getImg(True, size=[360, 240])  # Get a fresh frame from the webcam module
        frame = np.asarray(frame)

        classIds, confs, bbox = net.detect(frame, confThreshold=0.5)
        if len(classIds) != 0:
            for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                cv2.rectangle(frame, box, color=(0, 255, 0), thickness=3)
                cv2.putText(frame, classnames[classId - 1],
                            (box[0] + 10, box[1] + 20),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), thickness=2)

        if not img_queue.full():  # If the queue is not full, update the image
            img_queue.put(frame)

# TFLite Thread
def tflite_inference():
    global maxThrottle
    while True:
        if not img_queue.empty():  # Check if there's an image in the queue
            img = img_queue.get()  # Get the latest image from the queue

            img_resized = cv2.resize(img, (240, 120))
            img_resized = np.asarray(img_resized)
            img_resized = preProcess(img_resized)
            img_resized = np.expand_dims(img_resized, axis=0).astype(np.float32)

            interpreter.set_tensor(input_details[0]['index'], img_resized)
            interpreter.invoke()

            steering = interpreter.get_tensor(output_details[0]['index'])[0]
            throttle = 0
            throttle = throttle * ThrottleSen
            print(f'Steering: {steering * steeringSen}, Throttle: {throttle * 1}')
            
            if -1 <= throttle <= 1 and -1 <= steering <= 1:
                motor.move(maxThrottle, -steering * steeringSen, 0)
            else:
                motor.stop(500)
                print("Motor stopped")

# Main Function
if __name__ == "__main__":
    # Start background threads
    thread1 = threading.Thread(target=object_detection)
    thread2 = threading.Thread(target=tflite_inference)

    thread1.start()
    thread2.start()

    while True:
        if not img_queue.empty():  # Check if there's an image to show
            img = img_queue.get()
            cv2.imshow('Object Detection', img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Ensure threads complete before exiting
    thread1.join()
    thread2.join()

    cv2.destroyAllWindows()
