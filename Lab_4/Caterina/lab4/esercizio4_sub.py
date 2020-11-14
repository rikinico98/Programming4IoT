from MyMQTT import *
import time

class SensorSub():
    def __init__(self, sensorID, topic, broker, port):
        self.topic = topic
        self.client = MyMQTT(sensorID,broker,port,self)
    

    def start(self):
        self.client.start()
        self.client.mySubscribe(self.topic)
    
    def stop(self):
        self.client.stop()        
    
    def notify(self,topic,msg):
        self.payload=json.loads(msg)
        state = self.payload["e"][0]["r"]
        value = self.payload["e"][0]["v"]
        if state == "d":
            print(f"Warning! The value {value} bpm is dangerous at rest!")
        if state == "s" and value> 185:
            print(f"Warning! The value {value} bpm is dangerous during sport!")



if __name__ == '__main__':
    sensor = SensorSub('sensor2', 'Caterina/sensor_heart_rate/check',"mqtt.eclipse.org", 1883)
    sensor.start()
    while True:
        time.sleep(1)
    sensor.stop()