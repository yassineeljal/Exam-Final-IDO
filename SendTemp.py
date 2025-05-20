import paho.mqtt.client as pmc
from time import sleep
import time
import pigpio 
from pigpio_dht import DHT11
import threading
from flask import Flask, jsonify, request


gpio = 4
sensor = DHT11(gpio)

BROKER = "mqttbroker.lan"
PORT = 1883
TOPIC = "final/takfayassine/T"
TOPIC2 = "final/takfayassine/H"
BOUTON=3

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
TEMPERATURE = str(result.get("temp_c"))
HUMIDITY = str(result.get("humidity"))
ETAT = True





app = Flask(__name__)
pi = pigpio.pi()

@app.route('/donnees',methods=['GET'])
def get_temp():
  global TEMPERATURE, HUMIDITY
  return jsonify({
     'T': TEMPERATURE,
     'H': HUMIDITY
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
                        break
                    else:
                        ETAT = True
                        print("Programme mis en start")
                        break
                else:
                    continue


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
            countdown(30)
            result = sensor.read()
            TEMPERATURE = str(result.get("temp_c"))
            HUMIDITY = str(result.get("humidity"))
            client.publish(TOPIC, TEMPERATURE)
            client.publish(TOPIC2, HUMIDITY)  
            print("Les infos ont été envoyées (30sec)")

        else:
            continue

chrono = threading.Thread(target=SendDataEach30sec)   
chrono.start()     

hold_button = threading.Thread(target=Button_hold)
hold_button.start()

press_button = threading.Thread(target=Button_press)
press_button.start()
            

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=3000)
