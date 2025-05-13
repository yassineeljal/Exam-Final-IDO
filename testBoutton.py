import pigpio
import time

pi = pigpio.pi()

#3
BUTTON = 3
pi = pigpio.pi()
pi.set_mode(BUTTON,pigpio.INPUT)

while True:
    if(pi.read(BUTTON) == 0):
        start = time.time()
        while True:
            if(pi.read(BUTTON) == 1):
                end = time.time()
                if (end - start >= 2):
                    print("long")
                    break
                else:
                    print("court")
                    break