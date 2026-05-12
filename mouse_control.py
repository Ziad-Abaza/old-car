import pygame
import WebcamModule as wM
import DataCollectionModule as dcM
import motormodule as Motor
import cv2
import numpy as np
from time import sleep

maxThrottle = 0.25
record = 0

# Initialize pygame and create a window
def init():
    pygame.init()
    global win, display_width, display_height
    display_width, display_height = 240, 120
    win = pygame.display.set_mode((display_width, display_height))

# Function to get the state of a key
def getKey(keyName):
    ans = False
    keyInput = pygame.key.get_pressed()
    myKey = getattr(pygame, f'K_{keyName}')
    if keyInput[myKey]:
        ans = True
    return ans

def get_keyboard_and_mouse_input():
    steering = 0
    throttle = 0

    if getKey('w') or getKey('UP'):
        throttle = maxThrottle
        mouse_x, _ = pygame.mouse.get_pos()
        steering = (mouse_x / 240) * 2 - 1
    else:
        throttle = 0
        steering = 0

    return {'steering': steering, 'throttle': throttle}

init()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            cv2.destroyAllWindows()
            exit()

    key_input = get_keyboard_and_mouse_input()
    steering = key_input['steering']
    throttle = key_input['throttle']

    if getKey('c'):
        if record == 0:
            print('Recording Started ...')
        record += 1
        sleep(0.300)
    if record == 1 and throttle != 0:
        img = wM.getImg(True, size=[240, 120])
        dcM.saveData(img, steering)
    elif record == 2:
        dcM.saveLog()
        record = 0

    print("throttle: ", throttle)
    print("steering: ", steering)
    Motor.move(throttle, -steering, 0.1)

    # Show the control window with the current camera frame
    img = wM.getImg(True, size=[240, 120])
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (display_width, display_height))
    img = np.rot90(img)
    img = pygame.surfarray.make_surface(img)
    win.blit(img, (0, 0))
    pygame.display.update()

    if getKey('q'):
        break

pygame.quit()
cv2.destroyAllWindows()
