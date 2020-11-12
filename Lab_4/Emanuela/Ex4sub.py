#Receives temperature values, prints these on screen and save these on a json file called temp_log.json

from classMQTT import *
import json
import time

class heartRateReceiver():
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

    def notify(self,topic,msg):
        payload=json.loads(msg)
        new_status=payload["value"]
        self.status=new_status
        pubID=payload["clientID"]
        timestamp=payload["timestamp"]
        if payload["range"] == "danger":
            print(f"DANGER!!!!!! {new_status} at {timestamp} by {pubID}")

if __name__=="__main__":
    conf=json.load(open("settings.json"))
    broker=conf["broker"]
    port=conf["port"]
    myHeart=heartRateReceiver("heartRateReceiver287728","IoT/ManuelaVigl/heartRate",broker,port)
    myHeart.start()
    t_end = time.time() + 60 * 3
    while time.time() < t_end:
        time.sleep(2.5)
    myHeart.stop()