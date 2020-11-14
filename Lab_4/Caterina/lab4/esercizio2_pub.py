from MyMQTT import *
import numpy as np
import time
import random

#qui creo il publisher

class SensorPublisher():
    def __init__(self, sensorID, topic, broker, port):
        self.client = MyMQTT(sensorID,broker,port,None)
        self.topic = topic
        #senML format
        self.__message={
                        "bn": sensorID,
                        "e": [{
                            "n": "heart rate",
                            "u": "bpm",
                            "t": "",
                            "v": 60.1
                            }]
                        }
    def SendData(self):
        message = self.__message
        message["e"][0]["t"] = str(time.asctime( time.localtime(time.time())))
        mu, sigma = 120, 20
        # mean and standard deviation
        message["e"][0]["v"] = random.choice(np.random.normal(mu, sigma, 1000))
        print(message["e"][0]["v"])
        self.client.myPublish(self.topic, message)
    
    def start(self):
        self.client.start()
    
    def stop(self):
        self.client.stop()

if __name__ == '__main__':
    sensor = SensorPublisher('sensor1', 'Caterina/sensore/prova',"mqtt.eclipse.org", 1883)
    sensor.start()
    end = time.time() + 120 #per due minuti
    while time.time() < end:
        sensor.SendData() 
        time.sleep(5)#ogni 5 secondi
    sensor.stop()