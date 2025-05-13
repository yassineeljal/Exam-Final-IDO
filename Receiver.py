import paho.mqtt.client as pmc
import pigpio

BROKER = "mqttbroker.lan"
PORT = 1883
TOPIC = "final/+/T"
TOPIC2 = "final/+/H"


LED_ROUGE = 19
LED_BLEU = 26
LED_BLANCHE = 13


pi = pigpio.pi()

pi.set_mode(LED_BLANCHE, pigpio.OUTPUT)
pi.set_mode(LED_ROUGE, pigpio.OUTPUT)
pi.set_mode(LED_BLEU, pigpio.OUTPUT)

def connexion(client, userdata, flags, code, properties):
    if code == 0:
        print("Connecté")
    else:
        print("Erreur code %d\n", code)

def reception_msg(cl,userdata,msg):
    if (client.publish(TOPIC, TOPIC2)):
        if (max((client.publish(TOPIC, "TEMPERATURE")))):
            pi.write(LED_ROUGE, 1)
            pi.sleep(2)
            pi.write(LED_ROUGE, 0)
        elif (max((client.publish(TOPIC2, "HUMIDITY")))):
            pi.write(LED_ROUGE, 1)
            pi.sleep(2)
            pi.write(LED_ROUGE, 0)
        else:
            print("error")
        
        
        print("Reçu:",msg.payload.decode())

client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
client.on_connect = connexion
client.on_message = reception_msg

client.connect(BROKER,PORT)
client.subscribe(TOPIC)
client.subscribe(TOPIC2)
client.loop_forever()



