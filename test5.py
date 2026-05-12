import cv2
import numpy as np
import math
import time
from picamera2 import Picamera2
from gpiozero import Motor
from fractions import Fraction

# Initialize camera
cam = Picamera2()
cam.preview_configuration.main.size = (480, 360)
cam.preview_configuration.main.format = "RGB888"
cam.start()

# Initialize motors
right = Motor(forward=17, backward=27)
left = Motor(forward=5, backward=6)

# Parameters for image processing
lower_left_line = np.array([0, 0, 200])  # white
upper_left_line = np.array([180, 30, 255])  # white
lower_right_line = np.array([20, 100, 100])  # yellow
upper_right_line = np.array([30, 255, 255])  # yellow
lower_red = np.array([0, 100, 100])
upper_red = np.array([10, 255, 255])

# PID control parameters
speed = 0.25
kp = 0.4
kd = kp * 0.65

# Global movement flag
move = True

def detect_edges(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    return edges

def region_of_interest(edges):
    height, width = edges.shape
    mask = np.zeros_like(edges)
    vertices = np.array([[(0, height), (width/3, height/2), (width*2/3, height/2), (width, height)]], dtype=np.int32)
    cv2.fillPoly(mask, vertices, 255)
    cropped_edges = cv2.bitwise_and(edges, mask)
    return cropped_edges

def detect_line_segments(cropped_edges, lower_left_line, upper_left_line, lower_right_line, upper_right_line):
    rho = 1
    theta = np.pi / 180
    min_threshold = 30
    cropped_edges_bgr = cv2.cvtColor(cropped_edges, cv2.COLOR_GRAY2BGR)
    hsv = cv2.cvtColor(cropped_edges_bgr, cv2.COLOR_BGR2HSV)
    left_line = cv2.inRange(hsv, lower_left_line, upper_left_line)
    right_line = cv2.inRange(hsv, lower_right_line, upper_right_line)
    mask = cv2.bitwise_or(left_line, right_line)
    line_segments = cv2.HoughLinesP(mask, rho, theta, min_threshold, np.array([]), minLineLength=20, maxLineGap=500)
    return line_segments

def average_slope_intercept(frame, line_segments):
    lane_lines = []
    if line_segments is None:
        return lane_lines
    height, width, _ = frame.shape
    left_fit = []
    right_fit = []
    boundary = 1/3
    left_region_boundary = width * (1 - boundary)
    right_region_boundary = width * boundary
    for line_segment in line_segments:
        for x1, y1, x2, y2 in line_segment:
            if x1 == x2:
                continue
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - (slope * x1)
            if slope < 0 and x1 < left_region_boundary and x2 < left_region_boundary:
                left_fit.append((slope, intercept))
            elif slope > 0 and x1 > right_region_boundary and x2 > right_region_boundary:
                right_fit.append((slope, intercept))
    if left_fit:
        lane_lines.append(make_points(frame, np.average(left_fit, axis=0)))
    if right_fit:
        lane_lines.append(make_points(frame, np.average(right_fit, axis=0)))
    return lane_lines

def make_points(frame, line):
    height, width, _ = frame.shape
    slope, intercept = line
    y1 = height
    y2 = int(y1 / 2)
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
                length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                color = (0, 255, 255) if length >= 780 else (0, 255, 0)
                cv2.line(line_image, (x1, y1), (x2, y2), color, line_width)
    return cv2.addWeighted(frame, 0.8, line_image, 1, 1)

def display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=5):
    heading_image = np.zeros_like(frame)
    height, width, _ = frame.shape
    steering_angle_radian = steering_angle / 180.0 * math.pi
    x1, y1 = width // 2, height
    x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
    y2 = height // 2
    cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
    cv2.putText(heading_image, f"Angle: {round(steering_angle, 2)}°", (x2 + 10, y2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    return cv2.addWeighted(frame, 0.8, heading_image, 1, 1)

def control_steering(frame, lane_lines):
    height, width, _ = frame.shape
    center_x = width // 2
    if len(lane_lines) == 2:
        left_x = (lane_lines[0][0][0] + lane_lines[0][0][2]) // 2
        right_x = (lane_lines[1][0][0] + lane_lines[1][0][2]) // 2
        lane_center_x = (left_x + right_x) // 2
    elif len(lane_lines) == 1:
        lane_center_x = (lane_lines[0][0][0] + lane_lines[0][0][2]) // 2
    else:
        return 90
    error = center_x - lane_center_x
    steering_angle = 90 + 0.1 * error
    return steering_angle

def detect_red_line(frame, lower_red, upper_red):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_red, upper_red)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if h < w and h > 10:
            return True
    return False

def main():
    global move
    global stop = False
    start_time = time.time()
    frame_count = 0
    while True:
        frame = cam.capture_array()
        frame = cv2.flip(frame, -1)
        edges = detect_edges(frame)
        roi = region_of_interest(edges)
        line_segments = detect_line_segments(roi, lower_left_line, upper_left_line, lower_right_line, upper_right_line)
        lane_lines = average_slope_intercept(frame, line_segments)
        lane_lines_image = display_lines(frame, lane_lines)
        steering_angle = control_steering(frame, lane_lines)
        heading_image = display_heading_line(lane_lines_image, steering_angle)
        red_line = detect_red_line(frame, lower_red, upper_red)

        if red_line:
            right.stop()
            left.stop()
            stop = True
            print("stop")
            
            # time.sleep(5)
            # print("move")
            # move = True
            # time.sleep(5)
        if stop:

            move = False
        if move:
            if steering_angle > 90:
                left.forward(speed)
                right.backward(speed)
            elif steering_angle < 90:
                right.forward(speed)
                left.backward(speed)
            else:
                left.forward(speed)
                right.forward(speed)

        cv2.imshow("heading line", heading_image)
        key = cv2.waitKey(1)
        if key == 32:
            break

        frame_count += 1
        if frame_count % 10 == 0:
            end_time = time.time()
            elapsed_time = end_time - start_time
            fps = frame_count / elapsed_time
            print(f"FPS: {fps:.2f}")
            start_time = time.time()
            frame_count = 0

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
