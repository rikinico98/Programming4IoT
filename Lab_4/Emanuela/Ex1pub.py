#Emulate a temperature sensor that publish random values in the range [–10,39] every 5 seconds for 2 minutes

from classMQTT import *
import json
import time
import random

class temperatureSensor():

	def __init__(self,clientID,topic,broker, port):
		self.client=MyMQTT(clientID,broker,port,None)
		self.topic=topic
		self.__message={"clientID":clientID,"n":"read temperature value","value":None,"timestamp":'',"unit":"Cel"}
	
	def start(self):
		self.client.start()

	def stop(self):
		self.client.stop()

	def publish(self,value):
		message=self.__message
		message['value']=value
		message["timestamp"]=str(time.time())
		self.client.myPublish(self.topic,message)

if __name__ == "__main__":
	conf=json.load(open("settings.json"))
	broker=conf["broker"]
	port=conf["port"]
	myTempSensor = temperatureSensor("temperatureSensor287728","IoT/ManuelaVigl/temperature",broker,port)
	myTempSensor.client.start()

	t_end = time.time() + 60 * 2
	while time.time() < t_end:
		myTempSensor.publish(random.uniform(-10,39))
		time.sleep(5)
	
	myTempSensor.client.stop()