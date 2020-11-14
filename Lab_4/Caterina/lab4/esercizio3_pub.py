from MyMQTT import *
import numpy as np
import time
import random

#qui creo il publisher

class SensorPublisher():
    def __init__(self, sensorID, topic, broker, port):
        self.client = MyMQTT(sensorID,broker,port,None)
        self.topic = topic
        
    def SendData(self, message):
        self.client.myPublish(self.topic, message)
        print(message)
    
    def start(self):
        self.client.start()
    
    def stop(self):
        self.client.stop()

if __name__ == '__main__':
    sensor = SensorPublisher('sensor1', 'Caterina/sensore/prova',"mqtt.eclipse.org", 1883)
    sensor.start()
    payload = json.load(open("hr_log.json"))
    for element in payload:
        sensor.SendData(json.dumps(element)) 
        time.sleep(3)#ogni 5 secondi
    sensor.stop()