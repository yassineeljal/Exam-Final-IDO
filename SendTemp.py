# Code de Yassine
import paho.mqtt.client as pmc
from time import sleep
import time
import pigpio 
from pigpio_dht import DHT11
import threading
from flask import Flask, jsonify, request


gpio = 4
BROKER = "mqttbroker.lan"
PORT = 1883
TOPIC = "final/takfayassine/T"
TOPIC2 = "final/takfayassine/H"
BOUTON=3
LED_BLANCHE = 13

pi = pigpio.pi()
pi.set_mode(BOUTON,pigpio.INPUT)
pi.set_mode(LED_BLANCHE, pigpio.OUTPUT)


def connexion(client, userData, flags, code, proprietes):
    if code == 0:
        print("Connexion OK")
    else:
        print("Erreur connexion code: ", code)
    
sensor = DHT11(gpio,timeout_secs=1)
result = sensor.read()      



client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
client.on_connect = connexion
client.connect(BROKER,PORT)

pi = pigpio.pi()
pi.set_mode(BOUTON,pigpio.INPUT)
TEMPERATURE = str(result.get("temp_c"))
HUMIDITY = str(result.get("humidity"))
ETAT = True





app = Flask(__name__)
pi = pigpio.pi()

@app.route('/donnees',methods=['GET'])
def get_temp():
  global TEMPERATURE, HUMIDITY
  return jsonify({
     'T': str(result.get("temp_c")),
     'H': str(result.get("humidity"))
  })

@app.route('/etat', methods=['POST'])
def set_etat():
    global ETAT
    if request.method == "POST":
      json = request.get_json()
      if "etat" in json:
        if json["etat"] == 1:
            ETAT = True
        elif json["etat"] == 0:
            ETAT = False
        else:
            return jsonify({'Erreur': 'Mauvaise valeur'}),500
      else:
        return jsonify({'Erreur': 'Mauvais attribut'}),500
    else:
      return jsonify({'Erreur': 'Requetes POST seulement'}),500
    return jsonify({'Etat': json["etat"]}),200





def Button_hold():
    while True:
        global ETAT
        if(pi.read(BOUTON) == 0):
            start = time.time()
            while pi.read(BOUTON) == 0:
                if(time.time() - start >= 2):
                    if(ETAT):
                        ETAT = False
                        print("Programme mis en pause")
                        sleep(0.1)
                        break
                    else:
                        ETAT = True
                        print("Programme mis en start")
                        sleep(0.1)
                        break
                else:
                    sleep(0.5)
                    continue


def Open_led():
    while True:
        if pi.read(LED_BLANCHE) == 0 and ETAT:
            pi.write(LED_BLANCHE, 1) 
        elif pi.read(LED_BLANCHE) == 1 and not ETAT:
            pi.write(LED_BLANCHE, 0) 
        




def Button_press():
    while True:
        global ETAT, TEMPERATURE, HUMIDITY
        if (ETAT):
            if(pi.read(BOUTON) == 0):
                while True:
                    if(pi.read(BOUTON) == 1):
                        result = sensor.read()
                        TEMPERATURE = str(result.get("temp_c"))
                        HUMIDITY = str(result.get("humidity"))
                        client.publish(TOPIC, TEMPERATURE)
                        client.publish(TOPIC2, HUMIDITY)  
                        print("Les infos ont été envoyées (button)")
                        break
        else:
            sleep(0.5)
            continue


#https://www.geeksforgeeks.org/how-to-create-a-countdown-timer-using-python/
def countdown(t): 
    global ETAT
    while t: 
        mins, secs = divmod(t, 60) 
        timer = '{:02d}:{:02d}'.format(mins, secs) 
        print(timer, end="\r") 
        sleep(1) 
        t -= 1

def SendDataEach30sec():
    while True:
        global ETAT, TEMPERATURE, HUMIDITY
        if (ETAT):
            sleep(0.5)
            countdown(30)
            result = sensor.read()
            TEMPERATURE = str(result.get("temp_c"))
            HUMIDITY = str(result.get("humidity"))
            sleep(0.1)
            client.publish(TOPIC, TEMPERATURE)
            client.publish(TOPIC2, HUMIDITY)  
            print("Les infos ont été envoyées (30sec)")

        else:
            sleep(0.5)
            continue


chrono = threading.Thread(target=SendDataEach30sec)   
hold_button = threading.Thread(target=Button_hold)
press_button = threading.Thread(target=Button_press)
openLed = threading.Thread(target=Open_led)


chrono.start()   
sleep(0.5)
press_button.start()
sleep(0.5)
hold_button.start()
sleep(0.5)
openLed.start()
            

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=3000)

    