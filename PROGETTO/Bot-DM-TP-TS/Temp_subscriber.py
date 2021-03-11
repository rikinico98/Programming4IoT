import paho.mqtt.client as PahoMQTT
import json
import time
import requests
#Subscriber con MQTT
class SensorSubscriber():
    def __init__(self, clientID, broker, port, topic):
        self.topic = topic
        self.notifier = self
        self.clientID = clientID
        self.broker = broker
        self.port = port
        self.client = PahoMQTT.Client(clientID, True)
        self.client.on_message = self.myOnMessageReceived
        self.channelID = 1321136 #va letto dal catalog
        self.apikey = 'ZVBAO2QDON8B19X0' #va letto dal Catalog 
        self.baseURL = f"https://api.thingspeak.com/update?api_key={self.apikey}" #va letto dal Catalog
    def myOnMessageReceived(self, paho_mqtt , userdata, msg):
        self.notifier.notify(msg.topic, msg.payload)
    def start(self):
        self.client.connect(self.broker , self.port)
        self.client.loop_start()
        self.client.subscribe(self.topic, 2)  
        print("subscribed to %s" % (self.topic))
    def stop(self):
        self.client.unsubscribe(self._topic)
        self.client.loop_stop()
        self.client.disconnect()
    def notify(self,topic,msg):
        self.payload=json.loads(msg)
        value = self.payload['e'][0]['v']
        r = requests.get(self.baseURL+f'&field1={value}')

if __name__ == '__main__':
    #anche questi vanno presi dal Catalog
    #broker = requests.get("...catalog/msg_broker")
    #port = requests.get("...catalog/port")
    #topic = requests.get("...catalog/.../topic")
    sensor = SensorSubscriber('client1_prova_cate',"test.mosquitto.org", 1883, 'cate/temperatura/sensore/#')
    sensor.start()
    while True: #pubblica in continuazione
        time.sleep(1)
    sensor.stop()

