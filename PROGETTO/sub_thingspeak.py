# Receives messages from smoke sensor
# Rise telegram alarms if smoke detected is too high 


from MyMQTT import *
import threading
import json
import time
import requests

def _Findparametrs():
    r_thingspeak = requests.get(f'http://127.0.0.1:8070/catalog/Thingspeak_API')
    r_thingspeak1 = json.dumps(r_thingspeak.json(),indent=4)
    thinspeak_param = json.loads(r_thingspeak1)
    topic=thinspeak_param["Thingspeak_API"]["mqttTopicThingspeak"]
    thinkspeak_id= thinspeak_param["Thingspeak_API"]["clientID_Thingspeak_MQTT"]
    r_broker = requests.get(f'http://127.0.0.1:8070/catalog/MQTT_utilities')
    j_broker = json.dumps(r_broker.json(),indent=4)
    d_broker = json.loads(j_broker)
    broker = d_broker["MQTT_utilities"]["msgBroker"]
    port = d_broker["MQTT_utilities"]["port"]
    dict_return={"topic":topic,"thinkspeak_id":thinkspeak_id,"broker":broker,"port":port}
    return dict_return
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
        
    def sendThingSpeak(self):
        print(self.field,self.value)
        if len(self.field) > 0: 
            print(self.TS_api[0])
            r = requests.get(f'https://api.thingspeak.com/update?api_key={self.TS_api[0]}'+f'&{self.field[0]}={self.value[0]}') 
            self.field.pop(0)
            self.value.pop(0)
            self.TS_api.pop(0)

if __name__ == '__main__':
    parameters=_Findparametrs()
    sensor = SensorSubscriber(parameters["thinkspeak_id"],parameters["broker"], parameters["port"], parameters["topic"])
    sensor.start()
    while True: #pubblica in continuazione
        time.sleep(15)
        sensor.sendThingSpeak()
    sensor.stop()




