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
                            "r": "",
                            "v": 60.1
                            }]
                        }
    def SendData(self, hr_range):
        message = self.__message
        message["e"][0]["t"] = str(time.asctime( time.localtime(time.time())))
        if hr_range == 'r':
            mu, sigma = 70, 10
            message["e"][0]["v"] = random.choice(np.random.normal(mu, sigma, 1000))  
            message["e"][0]["r"] = hr_range  
        elif hr_range == 's':
            message["e"][0]["v"] = random.choice(np.random.chisquare(170,1000)) 
            message["e"][0]["r"] = hr_range 
        else:
            message["e"][0]["v"] = random.choice(np.random.chisquare(160,1000)) 
            message["e"][0]["r"] = hr_range 
            
        # mean and standard deviation
        
        print(message["e"][0]["v"])
        self.client.myPublish(self.topic, message)
    
    def start(self):
        self.client.start()
    
    def stop(self):
        self.client.stop()

if __name__ == '__main__':
    sensor = SensorPublisher('sensor_heart_rate', 'Caterina/sensor_heart_rate/check',"mqtt.eclipse.org", 1883)
    sensor.start()
    while True:
        hr_range = input("select:\n\tq: quit the client\nor\nselect a range:\n\tr: resting\n\ts: sport\n\td: dangerous\n")
        if hr_range == 'r':
            sensor.SendData(hr_range) 
            time.sleep(2)
        elif hr_range == 's':
            sensor.SendData(hr_range) 
            time.sleep(2)
        elif hr_range == 'd':
            sensor.SendData(hr_range) 
            time.sleep(2)
        elif hr_range == 'q':
            break
        else:
            print('wrong command! retry!')
    sensor.stop()