import motormodule as Motor
import keyboard as kp

kp.init()
# while True:
#     Motor.move(0.5,0.3,2)
#     Motor.stop(2)

def main():
    # print(kp.getKey('s'))
    # if(kp.getKey('s')):
    #     Motor.move(-0.5,0,0.1)
    if(kp.getKey('a') or kp.getKey('LEFT')):
        Motor.move(0.7,0.2,0.1)
    elif(kp.getKey('d') or kp.getKey('RIGHT')):
        Motor.move(0.7,-0.2,0.1)
    elif(kp.getKey('w') or kp.getKey('UP')):
        Motor.move(0.7,0,0.1)
    else:
        Motor.stop(0.1)
if __name__ == '__main__':
    while True:
        main()