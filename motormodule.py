from gpiozero import Motor
from time import sleep

# left = Motor(forward=17,backward=27)
# right = Motor(forward=5,backward=6)
# Define motor pins (adjust based on your motor driver board)
# motor = Motor(left=(17, 27), right=(5, 6))  # Replace with your pin assignments
left = Motor(forward=17,backward=27)
right = Motor(forward=5,backward=6)
# Define movement functions using gpizero's intuitive syntax

def move(speed=0.5, turn=0, duration=2):
    """Controls motor movement with speed, turn (direction), and duration."""

    # Validate speed and turn values (optional)
    if speed < -1 or speed > 1:
        raise ValueError("Speed must be between -1 and 1")
    if turn < -1 or turn > 1:
        raise ValueError("Turn must be between -1 and 1")

    # Calculate individual motor speeds based on speed and turn
    left_speed = speed - turn
    right_speed = speed + turn

    # Set motor speeds and direction (forward or backward)
    # left.forward(abs(left_speed) * (left_speed if left_speed > 0 else -1))
    # right.forward(abs(right_speed) * (right_speed if right_speed > 0 else -1))

    if left_speed > 0:
        left.forward(min(left_speed, 1))
    else:
        left.backward(min(-left_speed, 1))
    
    if right_speed > 0:
        right.forward(min(right_speed, 1))
    else:
        right.backward(min(-right_speed, 1))

    # Move for the specified duration
    sleep(duration)

def stop(duration=2):
    """Stops both motors."""
    left.stop()
    right.stop()
    sleep(duration)

# Example usage
if __name__ == "__main__":
    move(0.6, 0)  # Move forward at 60% speed (straight)
    stop()
    move(-0.5, 0.2)  # Move backward at 50% speed, turning slightly right
    stop()