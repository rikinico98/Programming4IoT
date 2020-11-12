#Emulate a temperature sensor that publish random values in the range [–10,39] every 5 seconds for 2 minutes

from classMQTT import *
import json
import time
import random
import numpy as np

class heartRateSensor():

	def __init__(self,clientID,topic,broker, port):
		self.client=MyMQTT(clientID,broker,port,None)
		self.topic=topic
		self.__message={"clientID":clientID,"n":"heart rate value","value":None,"timestamp":'',"unit":"bpm"}
	
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
	myHeartSensor = heartRateSensor("heartRate287728","IoT/ManuelaVigl/heartRate",broker,port)
	myHeartSensor.client.start()

	t_end = time.time() + 60 * 2
	shape, scale = 2., 2.  # mean=4, std=2*sqrt(2)
	vect = 8*np.random.gamma(shape, scale, 30)+55
	i = 0
	while time.time() < t_end:
		myHeartSensor.publish(vect[i])
		i = i+1
		time.sleep(5)
	
	myHeartSensor.client.stop()