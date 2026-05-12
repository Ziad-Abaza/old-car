import cv2
import numpy as np
from video import video  # Assuming video() function is defined in video.py
from gpiozero import Robot
from gpiozero import Motor

# Initialize the robot with GPIO pins for left and right motors
# bot = Robot(left=(17, 27), right=(5, 6))
left = Motor(forward=17,backward=27)
right = Motor(forward=5,backward=6)
# Define maximum and minimum speeds
MAX_SPEED = 0.44
MIN_SPEED = 0.22

# Function to set motor speeds based on angle
def set_motor_speeds(angle):
    if -10 <= angle <= 10:  # Straight
        left.forward(MIN_SPEED)
        right.forward(MIN_SPEED)
    elif angle < -10:       # Left turn
        left_speed = MAX_SPEED - (MAX_SPEED - MIN_SPEED) * (abs(angle) / 90)
        left.forward(MIN_SPEED)
        right.forward(MAX_SPEED)
    elif angle > 10:        # Right turn
        left.forward(MAX_SPEED)
        right.forward(MIN_SPEED)

# Function to perform bird's eye view perspective transformation
def bird_eye_view_transform(frame):
    # Define region of interest (ROI) points in the original image
    src_points = np.float32([(0, 400), (640, 400), (0, 480), (640, 480)])
    # Define corresponding points in the bird's eye view (top-down view)
    dst_points = np.float32([(0, 0), (640, 0), (0, 480), (640, 480)])
    # Compute perspective transform matrix
    M = cv2.getPerspectiveTransform(src_points, dst_points)
    # Perform perspective transformation to get bird's eye view
    bird_eye_view = cv2.warpPerspective(frame, M, (640, 480), flags=cv2.INTER_LINEAR)
    return bird_eye_view

# Main Loop
while True:
    # Read frame from the video source
    frame = video()
    if frame is None:
        break

    # Apply bird's eye view transformation
    bird_eye_frame = bird_eye_view_transform(frame)

    # Convert to grayscale
    gray = cv2.cvtColor(bird_eye_frame, cv2.COLOR_BGR2GRAY)

    # Apply binary threshold
    _, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)  # Adjust threshold as needed

    # Perform edge detection
    edges = cv2.Canny(binary, 50, 150)

    # Perform Hough Transform to detect lines
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=100)

    # Process detected lines
    if lines is not None:
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(bird_eye_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            # Calculate angle of the detected line
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            angles.append(angle)

        # Calculate median angle of all detected lines
        if angles:
            median_angle = np.median(angles)
            cv2.putText(bird_eye_frame, f"Angle: {median_angle:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            # Determine movement based on angle
            set_motor_speeds(median_angle)
        else:
            # If no lines are found, move forward at maximum speed
            left.forward(MIN_SPEED)
            right.forward(MIN_SPEED)
    else:
        # If no lines are found, move forward at maximum speed
        left.forward(MIN_SPEED)
        right.forward(MIN_SPEED)

    # Display the bird's eye view frame with detected lanes and angle information
    cv2.imshow('Bird Eye View Lane Detection', bird_eye_frame)

    # Check for 'q' key pressed to exit loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
cv2.destroyAllWindows()
