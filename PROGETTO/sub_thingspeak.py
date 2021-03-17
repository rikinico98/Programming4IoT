# Receives messages from smoke sensor
# Rise telegram alarms if smoke detected is too high 


from MyMQTT import *
import threading
import json
import time
import requests

class SensorSubscriber():
    def __init__(self, clientID, broker, port, topic):
        self.topic = topic
        self.notifier = self
        self.clientID = clientID
        self.broker = broker
        self.field=[]
        self.value=[]
        self.TS_api=[]
        self.port = port
        self.client = PahoMQTT.Client(clientID, True)
        self.client.on_message = self.myOnMessageReceived
        # self.channelID = 1321136 #va letto dal catalog
        # self.apikey = '4O6ZLEXF1XAQ933O' #va passata come messaggio 
        # self.baseURL = f"https://api.thingspeak.com/update?api_key={self.apikey}" #va passata come messaggio
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
        print(json.dumps(self.payload))
        self.TS_api.append(self.payload["TS_api"])
        self.field.append(self.payload["ThingSpeak_field"]) # devo avere in aggiunta al campo anche l'URL del canale ThingSpeak della stanza
        self.value.append(self.payload["v"])
        # print(field,value)
        # print(field,value)
    def sendThingSpeak(self):
        print(self.field,self.value)
        if len(self.field) > 0: 
            print(self.TS_api[0])
            r = requests.get(f'https://api.thingspeak.com/update?api_key={self.TS_api[0]}'+f'&{self.field[0]}={self.value[0]}') 
            self.field.pop(0)
            self.value.pop(0)
            self.TS_api.pop(0)

if __name__ == '__main__':
    #anche questi vanno presi dal Catalog
    #broker = requests.get("...catalog/msg_broker")
    #port = requests.get("...catalog/port")
    #topic = requests.get("...catalog/.../topic")
    sensor = SensorSubscriber('allsensor_sub_pob',"test.mosquitto.org", 1883, 'ThingSpeak/channel/allsensor')
    sensor.start()
    while True: #pubblica in continuazione
        time.sleep(15)
        sensor.sendThingSpeak()
    sensor.stop()




