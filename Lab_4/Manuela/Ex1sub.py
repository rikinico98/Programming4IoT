#Receives temperature values, prints these on screen and save these on a json file called temp_log.json

from classMQTT import *
import json
import time

class temperatureReceiver():
    def __init__(self,clientID,topic,broker, port):
        self.client=MyMQTT(clientID,broker,port,self)
        self.topic=topic
        self.status=None
        self.allMeasure = []
    
    def start(self):
        self.client.start()
        self.client.mySubscribe(self.topic)

    def stop(self):
        self.client.stop()
        jsonFile = open("temp_log.json","w")
        myDict = {
            "bn" : "http://example.org/sensor1/",
            "e" : self.allMeasure
        }
        jsonFile.write(json.dumps(myDict))
        jsonFile.close()

    def notify(self,topic,msg):
        payload=json.loads(msg)
        new_status=payload["value"]
        self.status=new_status
        pubID=payload["clientID"]
        timestamp=payload["timestamp"]
        print(f"The temperature is {new_status} at {timestamp} by {pubID}")
        myDict = {
            "n" : "temperature",
            "u" : "Cel", # measure unit
            "t" : timestamp,
            "v" : new_status
        }
        self.allMeasure.append(myDict)

if __name__=="__main__":
    conf=json.load(open("settings.json"))
    broker=conf["broker"]
    port=conf["port"]
    myTemp=temperatureReceiver("temperatureReceiver287728","IoT/ManuelaVigl/temperature",broker,port)
    myTemp.start()
    t_end = time.time() + 60 * 3
    while time.time() < t_end:
        time.sleep(3)
    myTemp.stop()