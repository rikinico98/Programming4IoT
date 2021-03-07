import paho.mqtt.client as PahoMQTT
import time
import random
import json

#simulatore di sensore di Temperatura MQTT publisher con libreria paho
class SensorPublisher():
    def __init__(self, sensorID, broker, port, topic): 
        self.client = PahoMQTT.Client(sensorID, True)
        self.broker = broker
        self.topic = topic
        self.port = port
        self.__message={
                            "bn": sensorID,
                            "e": [{
                                "n": "temperature",
                                "u": "Cel",
                                "t": "",
                                "v":0
                                }]
                        }
        self.client.on_connect = self.myOnConnect
    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        print ("Connected to %s with result code: %d" % (self.broker, rc))
    def SendData(self):
        message = self.__message
        message["e"][0]["t"] = str(time.asctime( time.localtime(time.time())))
        message["e"][0]["v"] = random.randint(-5, 25) #va cambiata secondo la temperatura che decidiamo
        self.client.publish(self.topic, json.dumps(message), 2)
    def start(self):
        self.client.connect(self.broker , self.port)
        self.client.loop_start()    
    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
if __name__ == '__main__':
    #vanno presi dal Catalog
    sensor = SensorPublisher('sensor1_prova_cate',"test.mosquitto.org", 1883, 'cate/temperatura/sensore/1')
    sensor.start()
    while True:
        sensor.SendData() 
        time.sleep(1)#ogni secondo
    sensor.stop()
