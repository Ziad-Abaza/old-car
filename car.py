# from gpiozero import Robot
# bot = Robot((27,17),(6,5))
from gpiozero import Motor


left = Motor(forward=17,backward=27)
right = Motor(forward=5,backward=6)
speed = 0.3
while True:
    user_input = input()
    if user_input == 'w':
        left.forward(speed)
        right.forward(speed)

    elif user_input == 's':
        left.backward(speed)
        right.backward(speed)
    elif user_input == 'a':
        left.backward(speed)
        right.forward(speed)
    elif user_input =='d':
        left.forward(speed)
        right.backward(speed)
    elif user_input =='c':
        left.stop()
        right.stop()