from MyMQTT import *
import random
import time

#qui creo il publisher

class SensorPublisher():
    def __init__(self, sensorID, topic, broker, port):
        self.client = MyMQTT(sensorID,broker,port,None)
        self.topic = topic
        #senML format
        self.__message={
                        "bn": sensorID,
                        "e": [{
                            "n": "temperature",
                            "u": "Cel",
                            "t": "",
                            "v":22.5
                            }]
                        }
    def SendData(self):
        message = self.__message
        message["e"][0]["t"] = str(time.asctime( time.localtime(time.time())))
        message["e"][0]["v"] = random.randint(-10,39)
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
