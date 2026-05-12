import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.losses import MeanSquaredError
import WebcamModule as wM
import motormodule as motor

#######################################
steeringSen = -0.75  # Steering Sensitivity
maxThrottle = 0.25  # Forward Speed %
ThrottleSen = 0.65
custom_objects = {'mse': MeanSquaredError()}
model = load_model('sss.h5', custom_objects=custom_objects)
model.compile(optimizer='adam', loss='mse')
######################################

def preProcess(img):
    img = img[54:120, :, :]
    img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    img = cv2.resize(img, (200, 66))
    img = img / 255
    return img

def main():
    while True:
        # Get image from webcam
        img = wM.getImg(True, size=[240, 120])
        img = np.asarray(img)
        
        # Process image and predict steering
        processed_img = preProcess(img)
        steering = model.predict(np.array([processed_img]))[0]
        throttle = maxThrottle * ThrottleSen

        print(f'Steering: {steering * steeringSen}, Throttle: {throttle}')

        # Motor control
        if np.all(throttle <= 1) and np.all(throttle >= -1) and np.all(steering <= 1) and np.all(steering >= -1):
            motor.move(maxThrottle, -steering[0] * steeringSen, 0)
        else:
            motor.stop(500)
            print("Stopped due to invalid steering or throttle values")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            motor.stop(500)
            break

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        motor.stop(500)
        print("Program stopped")