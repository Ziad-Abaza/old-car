import cv2
import numpy as np
import math
import time
from picamera2 import Picamera2
# import matpot
cam = Picamera2()

# cam.preview_configuration.main.size=(1920,1080)

cam.preview_configuration.main.size=(720,640)
cam.preview_configuration.main.format = "RGB888"
cam.start()
global red_roi
red_roi = np.array([[
            (0, 0),       # Top-left corner
    (0, 228),     # Bottom-left corner
    (1200, 228),  # Bottom-right corner
    (1200, 0)     # Top-right corner
    ]], np.int32)
def detect_edges(frame,lower_left_line, upper_left_line, lower_right_line, upper_right_line):
    # Convert image to grayscale
    # vertices = np.array([[
    #     (0, 0),       # Top-left corner
    #     (0, 100),     # Bottom-left corner
    #     (1200, 100),  # Bottom-right corner
    #     (1200, 0)  
    #    ]], dtype=np.int32)
    height = frame.shape[0]
    vertices = np.array([[
        (200, 0),       # Top-left corner
        (800, 400),     # Bottom-left corner
        (1200, 0)  # Bottom-right corner
        # (1200, 0)  
       ]], dtype=np.int32)
    cv2.fillPoly(frame, vertices, 0)
    vertices = np.array([[
        (0, 0),       # Top-left corner
        (0, 150),     # Bottom-left corner
        (1200, 0)  # Bottom-right corner
        # (1200, 0)  
       ]], dtype=np.int32)
    cv2.fillPoly(frame, vertices, 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    cv2.imshow("hsv", hsv)
    left_line = cv2.inRange(hsv, lower_left_line, upper_left_line)
    # cv2.imshow("left",left_line)
    right_line = cv2.inRange(hsv, lower_right_line, upper_right_line)

    mask = cv2.bitwise_or(left_line, right_line)
    cv2.imshow("lines", mask)
    # Convert image to grayscale
    
    # Apply Gaussian Blur
    blurred = cv2.GaussianBlur(mask, (5, 5), 0)
    
    # Detect edges using Canny edge detection
    edges = cv2.Canny(blurred, 50, 150) 
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow("edges", edges)
    return edges

def region_of_interest(edges):
    height, width = edges.shape
    mask = np.zeros_like(edges)

    # Define vertices of the region of interest (ROI)
    vertices = np.array([[
        (0, 100),
     (width/3, height),
      (width*2/3, height),
       (width, 100)
       ]], dtype=np.int32)
    
    # Fill the ROI with white color
    cv2.fillPoly(mask, vertices, 255)
    
    # Bitwise AND between edges image and ROI mask
    cropped_edges = cv2.bitwise_and(edges, mask)
    # cropped_edges = edges
    return cropped_edges

def detect_line_segments(cropped_edges):
    # Define parameters for Hough Line Transform 
    rho = 1  
    theta = np.pi / 180  
    min_threshold = 30  
    # cropped_edges_bgr = cv2.cvtColor(cropped_edges, cv2.COLOR_GRAY2BGR)
    # cv2.imshow("edges", cropped_edges_bgr)

    # cv2.imshow("t",mask)
    # Apply Hough Line Transform
    line_segments = cv2.HoughLinesP(cropped_edges, rho, theta, min_threshold, np.array([]), minLineLength=50, maxLineGap=150)

    return line_segments

def average_slope_intercept(frame, line_segments):
    lane_lines = []
    
    if line_segments is None:
        print("no line segments detected")
        return lane_lines

    height, width,_ = frame.shape
    left_fit = []
    right_fit = []

    boundary = 1/3
    left_region_boundary = width * (1 - boundary)
    right_region_boundary = width * boundary
    
    for line_segment in line_segments:
        for x1, y1, x2, y2 in line_segment:
            if x1 == x2:
                print("skipping vertical lines (slope = infinity")
                continue
            
            # Fit a line to the line segment
            fit = np.polyfit((x1, x2), (y1, y2), 1)
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - (slope * x1)
            
            # Classify lines into left and right based on slope and position
            if slope < 0:
                if x1 < left_region_boundary and x2 < left_region_boundary:
                    left_fit.append((slope, intercept))
            else:
                if x1 > right_region_boundary and x2 > right_region_boundary:
                    right_fit.append((slope, intercept))

    # Calculate average slope and intercept for left lane line
    left_fit_average = np.average(left_fit, axis=0)
    if len(left_fit) > 0:
        lane_lines.append(make_points(frame, left_fit_average))

    # Calculate average slope and intercept for right lane line
    right_fit_average = np.average(right_fit, axis=0)
    if len(right_fit) > 0:
        lane_lines.append(make_points(frame, right_fit_average))

    return lane_lines

def make_points(frame, line):
    height, width, _ = frame.shape
    
    slope, intercept = line
    
    y1 = height 
    y2 = int(y1 / 2)  
    
    # Avoid division by zero
    if slope == 0:
        slope = 0.1
        
    x1 = int((y1 - intercept) / slope)
    x2 = int((y2 - intercept) / slope)
    
    return [[x1, y1, x2, y2]]

def display_lines(frame, lines, line_color=(0, 255, 0), line_width=5):
    line_image = np.zeros_like(frame)
    
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                # Check if the line is small and dashed
                length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                print(length)
                if length < 780:
                    line_color = (0, 255, 0)  # Yellow 
                else:
                    line_color = (0, 255, 255)  # Green 
                cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
                
    line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    
    return line_image

def display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=5 ):
    heading_image = np.zeros_like(frame)
    height, width, _ = frame.shape
    
    steering_angle_radian = steering_angle / 180.0 * math.pi
    
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
    y2 = int(height / 2)
    
    cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
    heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)
    
    # Display the angle of the line
    font = cv2.FONT_HERSHEY_SIMPLEX
    org = (x2 + 10, y2)
    fontScale = 1
    color = (255, 255, 255)
    thickness = 2
    angle_text = f"Angle: {round(steering_angle, 2)}°"
    print(angle_text)
    cv2.putText(heading_image, angle_text, org, font, fontScale, color, thickness)
    
    return heading_image

def get_steering_angle(frame, lane_lines):
    height, width,_ = frame.shape
    
    if len(lane_lines) == 2:
        _, _, left_x2, _ = lane_lines[0][0]
        _, _, right_x2, _ = lane_lines[1][0]
        mid = int(width / 2)
        x_offset = (left_x2 + right_x2) / 2 - mid
        y_offset = int(height / 2)
        
    elif len(lane_lines) == 1:
        x1, _, x2, _ = lane_lines[0][0]
        x_offset = x2 - x1
        y_offset = int(height / 2)
        
    elif len(lane_lines) == 0:
        x_offset = 0
        y_offset = int(height / 2)
        
    angle_to_mid_radian = math.atan(x_offset / y_offset)
    angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)
    steering_angle = angle_to_mid_deg + 90

    return steering_angle

def detect_red_line(frame, lower_red, upper_red):
    height = frame.shape[0]
    width = frame.shape[1]
    roi = red_roi

    cv2.fillPoly(frame,roi,255)
    cv2.imshow("roi", frame)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_red, upper_red)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if h < w and h > 10 and h<50:  # Condition for detecting horizontal lines
            return True
    return False

# video = cv2.VideoCapture("test/WhatsApp Video 2024-05-01 at 15.18.04_c076843e.mp4")

speed = 8
lastTime = 0
lastError = 0

kp = 0.4
kd = kp * 0.65
def video(video):
    return video
from gpiozero import Motor


right = Motor(forward=17,backward=27)
left = Motor(forward=5,backward=6)

# bot = Robot((17,27),(5,6))
from fractions import Fraction
def control_steering(frame, lane_lines):
    height, width, _ = frame.shape
    center_x = width // 2

    if len(lane_lines) == 2:
        # Calculate the average position of the two lane lines
        left_x = (lane_lines[0][0][0] + lane_lines[0][0][2]) // 2
        right_x = (lane_lines[1][0][0] + lane_lines[1][0][2]) // 2
        lane_center_x = (left_x + right_x) // 2
    elif len(lane_lines) == 1:
        # If only one lane line is detected, assume it's the center
        lane_center_x = (lane_lines[0][0][0] + lane_lines[0][0][2]) // 2
    else:
        # If no lane lines are detected, keep the steering angle straight
        return 90
    
    # Calculate the error between the center of the frame and the lane center
    error = center_x - lane_center_x
    
    # Adjust the steering angle based on the error (proportional control)
    steering_angle = 90 + 0.1 * error
    
    return steering_angle

# Inside the main loop


start_time = time.time()
frame_count = 0
speed = 0.5


import threading

# Define a global variable to track if the vehicle should stop
stop_movement = False

def stop_motors():
    global stop_movement
    stop_movement = False
def movemotors(steering_angle):
    if steering_angle>90:
            # angle = Fraction(int(steering_angle), 90)
            # bot.right(0.3)
            # left.forward((angle.denominator*speed))
            # right.forward((angle.numerator*speed))
        angle = round(steering_angle, 2)
        low = 0.35 * math.cos((math.pi*angle)/180)-0.1
        left.forward(speed)
        right.forward(abs(low))
    elif steering_angle<90:
            # angle = Fraction((int(steering_angle), 90))
        angle = round(steering_angle, 2)
        low = 0.35 * math.cos((math.pi*angle)/180)-0.1
        right.forward(speed)
        left.forward(abs(low))
            # left.backward(speed)
            # right.forward(speed)
            # right.forward((angle.denominator*speed))
            # left.forward((angle.numerator*speed))
    else:
        left.forward(speed)
        right.forward(speed)
def set_red_roi():
    global red_roi
    red_roi = np.array([[
        (0, 0),       # Top-left corner
        (0, 228),     # Bottom-left corner
        (1200, 228),  # Bottom-right corner
        (1200, 0)     # Top-right corner
    ]], np.int32)
while True:
    frame = cam.capture_array()

    frame = cv2.flip(frame, -1)
    lower_left_line = np.array([0, 0, 255])  #white
    upper_left_line = np.array([180, 55, 255]) #white
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    lower_right_line = np.array([20, 100, 100])  #yellow
    upper_right_line = np.array([30, 255, 255]) #yellow
# lower_yellow = np.array([20, 100, 100])
# upper_yellow = np.array([30, 255, 255])
    cv2.imshow("original", frame)
    edges = detect_edges(frame, lower_left_line, upper_left_line, lower_right_line, upper_right_line)
    # cv2.imshow("fff", edges)
    roi = region_of_interest(edges)
    line_segments = detect_line_segments(roi)
    lane_lines = average_slope_intercept(frame, line_segments)
    lane_lines_image = display_lines(frame, lane_lines)
    # steering_angle = get_steering_angle(frame, lane_lines)
    steering_angle = control_steering(frame, lane_lines)

    heading_image = display_heading_line(lane_lines_image, steering_angle)


    frame_count += 1
    if frame_count % 10 == 0:  # Calculate FPS every 10 frames
        end_time = time.time()
        elapsed_time = end_time - start_time
        fps = frame_count / elapsed_time
        print(f"FPS: {fps:.2f}")
        start_time = time.time()
        frame_count = 0

    red_line = detect_red_line(frame ,lower_red,upper_red)
    if stop_movement:
        # If stop_movement is True, stop the motors
        left.stop()
        right.stop()
        # Reset stop_movement after 5 seconds
        threading.Timer(5, lambda: stop_motors()).start()
        # Set stop_movement back to False
        stop_movement = False
    
    if red_line:
        right.stop()
        left.stop()
        time.sleep(5)
        red_roi = np.array([[
        (0, 0),       # Top-left corner
        (0, 235),     # Bottom-left corner
        (1200, 235),  # Bottom-right corner
        (1200, 0)     # Top-right corner
        ]], np.int32)
        threading.Timer(5, lambda: set_red_roi()).start()
        movemotors(steering_angle)
        # time.sleep(10)

        # if not stop_movement:
        #     # If stop_movement is False, start a timer to resume movement after 5 seconds
        #     threading.Timer(5, lambda: stop_motors()).start()
        #     # Set stop_movement to True to prevent starting multiple timers
        #     stop_movement = True

    else:
        movemotors(steering_angle)

        
    cv2.imshow("heading line", heading_image)
    
    # key = cv2.waitKey(150)
    key = cv2.waitKey(1)
    if key == 32:
        break

video.release()
cv2.destroyAllWindows()