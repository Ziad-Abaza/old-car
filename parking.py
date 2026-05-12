import cv2
import numpy as np
import time

import WebcamModule as wM
import motormodule as motor

# Car control functions
def move_forward(speed=1):
    motor.move(speed, 0, 0)

def turn_left(angle=1):
    motor.move(0.25, angle, 0)

def turn_right(angle=1):
    motor.move(0.25, -angle, 0)

def stop():
    motor.move(0, 0, 0)
    print("Stopping the car")

# Image processing and line detection
def process_image(image):
    # Define the region of interest (ROI)
    height, width, _ = image.shape
    roi = image[:int(3*height/4), :]  # Crop the bottom quarter of the image
    
    # Convert to HSV color space
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    # Define range for blue color and create a mask
    lower_blue = np.array([100, 150, 0])
    upper_blue = np.array([140, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(roi, roi, mask=mask)
    
    # Convert the result to grayscale
    gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian Blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Use Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)
    
    # Apply Hough Line Transform
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, maxLineGap=50)
    
    return lines, roi

def draw_lines(image, lines):
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    return image

# Calculate centroid of the parking slot
def calculate_centroid(lines):
    if lines is None:
        return None
    
    x_coords = []
    y_coords = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        x_coords.extend([x1, x2])
        y_coords.extend([y1, y2])
    
    centroid_x = int(sum(x_coords) / len(x_coords))
    centroid_y = int(sum(y_coords) / len(y_coords))
    
    return (centroid_x, centroid_y)

# Simple navigation logic to move towards the centroid
def navigate_to_centroid(centroid, current_position):
    if centroid is None:
        return
    
    target_x, target_y = centroid
    current_x, current_y = current_position
    
    # Smooth movement towards the target
    while True:
        if abs(current_x - target_x) < 10 and abs(current_y - target_y) < 10:
            stop()
            break
        
        if current_x < target_x:
            turn_right(5)
            move_forward(1)
        elif current_x > target_x:
            turn_left(5)
            move_forward(1)
        else:
            move_forward(1)
        
        # Update current position (this should be based on sensor data in a real setup)
        current_x += 1  # Example update, replace with actual sensor data
        current_y += 1  # Example update, replace with actual sensor data
        
        time.sleep(0.1)

# Main function integrating the entire pipeline
def main():
    current_position = (0, 0)  # Starting position of the car (example)
    
    while True:
        # Capture image from the camera
        image = wM.getImg(True, size=[240, 120])
        
        # Process the image to detect lines
        lines, roi = process_image(image)
        
        # Draw lines on the image for visualization (optional)
        image_with_lines = draw_lines(roi, lines)
        cv2.imshow('Detected Lines', image_with_lines)
        cv2.waitKey(1)
        
        # Calculate the centroid of the parking slot
        centroid = calculate_centroid(lines)
        
        # Navigate the car to the centroid
        navigate_to_centroid(centroid, current_position)
        
        # Add a delay to control the loop frequency
        time.sleep(1)

if __name__ == "__main__":
    main()
