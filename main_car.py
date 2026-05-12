# from gpiozero import Motor

# Motor1 = Motor(17,27)

# motor2 = Motor(5,6)

# while True:
#     Motor1.forward()
from test3 import get_steering_angle
from gpiozero import Robot
bot = Robot((27,17),(6,5))

while True:
    test = round(get_steering_angle(), 2)

    print("test: ",test)
    if test == 90:
        bot.forward(0.25)
    elif test<90:
        bot.left(0.25)
    elif test>90:
        bot.right(0.25)
    # user_input = input()
    # if user_input == 'w':
    #     bot.backward(0.2)
    # elif user_input == 's':
    #     bot.forward(0.2)
    # elif user_input == 'a':
    #     bot.right(0.2)
    # elif user_input =='d':
    #     bot.left(0.2)
    # elif user_input =='c':
    #     bot.stop()

# import 