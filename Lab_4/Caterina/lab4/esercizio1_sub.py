from MyMQTT import *
import time

class SensorSub():
    def __init__(self, sensorID, topic, broker, port, sensorlist):
        self.sensorlist = sensorlist
        self.topic = topic
        self.client = MyMQTT(sensorID,broker,port,self)
    

    def start(self):
        self.client.start()
        self.client.mySubscribe(self.topic)
    
    def stop(self):
        self.client.stop()        
    
    def notify(self,topic,msg):
        self.payload=json.loads(msg)
        print(json.dumps(self.payload))
        self.sensorlist.append(self.payload)
        json.dump(self.sensorlist, open("json_log.json","w"))


if __name__ == '__main__':
    sensorlist = []
    sensor = SensorSub('sensor2', 'Caterina/sensore/prova',"mqtt.eclipse.org", 1883, sensorlist)
    sensor.start()
    while True:
        time.sleep(3)
    sensor.stop()
    
