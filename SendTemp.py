import paho.mqtt.client as pmc
from time import sleep
import pigpio 
from pigpio_dht import DHT11

gpio = 4
sensor = DHT11(gpio)

BROKER = "mqttbroker.lan"
PORT = 1883
TOPIC = "final/takfayassine/T"
TOPIC2 = "final/takfayassine/H"
BOUTON=3
LED =26

pi = pigpio.pi()
pi.set_mode(BOUTON,pigpio.INPUT)

def connexion(client, userData, flags, code, proprietes):
    if code == 0:
        print("Connexion OK")
    else:
        print("Erreur connexion code: ", code)
    
sensor = DHT11(gpio)
result = sensor.read()      


client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
client.on_connect = connexion
client.connect(BROKER,PORT)

pi = pigpio.pi()
pi.set_mode(BOUTON,pigpio.INPUT)
pi.set_pull_up_down(BOUTON,pigpio.PUD_UP)
TEMPERATURE = str(result.get("temp_c"))
HUMIDITY = str(result.get("humidity"))

#https://www.geeksforgeeks.org/how-to-create-a-countdown-timer-using-python/
def countdown(t): 
    while t: 
        if(pi.read(BOUTON)):
            result = sensor.read()
            TEMPERATURE = str(result.get("temp_c"))
            HUMIDITY = str(result.get("humidity"))
            client.publish(TOPIC, TEMPERATURE)
            client.publish(TOPIC2, HUMIDITY)    

        mins, secs = divmod(t, 60) 
        timer = '{:02d}:{:02d}'.format(mins, secs) 
        print(timer, end="\r") 
        sleep(1) 
        t -= 1

while True:
    try:
        countdown(30)
        TEMPERATURE = str(result.get("temp_c"))
        HUMIDITY = str(result.get("humidity"))
    except TimeoutError:
        print("Expired")

                
            
            
