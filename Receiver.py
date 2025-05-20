import paho.mqtt.client as pmc
import pigpio
import time

BROKER = "mqttbroker.lan"
PORT = 1883
TOPIC_T = "final/+/T"
TOPIC_H = "final/+/H"

LED_ROUGE = 19
LED_BLEU = 26
LED_BLANCHE = 13

hostname = "takfayassine" 
pi = pigpio.pi()
pi.set_mode(LED_ROUGE, pigpio.OUTPUT)
pi.set_mode(LED_BLEU, pigpio.OUTPUT)
pi.set_mode(LED_BLANCHE, pigpio.OUTPUT)

dictionnaire_temperature = {}
dictionnaire_humidite = {}
dernierEnvoiDeDonnees = 0

def connexion(client, userdata, flags, code, properties=None):
    if code == 0:
        print("Connecté au broker MQTT.")
        client.subscribe(TOPIC_T)
        client.subscribe(TOPIC_H)
    else:
        print(f"Erreur de connexion: code {code}")

def gestionLeds():
    if hostname in dictionnaire_temperature:
        temperatureMax = max(dictionnaire_temperature.values())
        if dictionnaire_temperature[hostname] == temperatureMax:
            pi.write(LED_ROUGE, 1)  
        else:
            pi.write(LED_ROUGE, 0)  
    else:
        pi.write(LED_ROUGE, 0)  

    if hostname in dictionnaire_humidite:
        humiditeMax = max(dictionnaire_humidite.values())
        if dictionnaire_humidite[hostname] == humiditeMax:
            pi.write(LED_BLEU, 1) 
        else:
            pi.write(LED_BLEU, 0) 
    else:
        pi.write(LED_BLEU, 0)  


def reception_msg(client, userdata, msg):
    global dernierEnvoiDeDonnees

    topic = msg.topic
    payload = msg.payload.decode()

    try:
        valeur = int(payload)
    except ValueError:
        print(f"Valeur non entière ignorée : {payload}")
        return

    parts = topic.split('/')
    if len(parts) != 3:
        print(f"Format de topic inattendu : {topic}")
        return

    host = parts[1]
    mesure = parts[2]


    print(f"Reçu de {host} | {mesure} = {valeur}")

    if mesure == "T":
        dictionnaire_temperature[host] = valeur
    elif mesure == "H":
        dictionnaire_humidite[host] = valeur
    else:
        return

    if host == hostname:
        dernierEnvoiDeDonnees = time.time()

    gestionLeds()

client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
client.on_connect = connexion
client.on_message = reception_msg
client.connect(BROKER, PORT)
client.loop_start()

try:
    while True:
        now = time.time()
        if now - dernierEnvoiDeDonnees <= 35:
            pi.write(LED_BLANCHE, 1) 
        else:
            pi.write(LED_BLANCHE, 0)  
        time.sleep(1)

except KeyboardInterrupt:
    print("Fin du programme.")
    pi.write(LED_ROUGE, 0)
    pi.write(LED_BLEU, 0)
    pi.write(LED_BLANCHE, 0)
    client.disconnect()
