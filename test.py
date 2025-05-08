import pigpio
from time import sleep

pi = pigpio.pi()

LED_ROUGE = 19
LED_BLEU = 26
LED_BLANCHE = 13

pi.set_mode(LED_BLANCHE, pigpio.OUTPUT)
pi.set_mode(LED_ROUGE, pigpio.OUTPUT)
pi.set_mode(LED_BLEU, pigpio.OUTPUT)

print("Allumage des LEDs pendant 5 secondes...")
for pin in led_pins:
    pi.write(pin, 1)  
sleep(5)

for pin in led_pins:
    pi.write(pin, 0)  

print("LEDs éteintes.")

pi.stop()
