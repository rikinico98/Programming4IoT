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
		self.__message={"clientID":clientID,"n":"heart rate value","value":None,"timestamp":'',"unit":"bpm", "range" : ""}
	
	def start(self):
		self.client.start()

	def stop(self):
		self.client.stop()

	def publish(self,value,mode):
		message=self.__message
		message['value']=value
		message["timestamp"]=str(time.time())
		if mode == 1:
			if value < 60 or value > 160:
				message["range"] = "danger"
			else:
				message["range"] = "sport"
		else:
			if value < 45 or value > 125:
				message["range"] = "danger"
			else:
				message["range"] = "rest"
		self.client.myPublish(self.topic,message)
		#print(f"Heart rate is {value} with mode {mode}")

if __name__ == "__main__":
	conf=json.load(open("settings4.json"))
	broker=conf["broker"]
	port=conf["port"]
	myHeartSensor = heartRateSensor("heartRate287728","IoT/ManuelaVigl/heartRate",broker,port)
	myHeartSensor.client.start()
	mode = conf["mode"]
	time.sleep(0.5)

	t_end = time.time() + 60 * 2
	shape, scaleRest = 2., 2.  # mean=4, std=2*sqrt(2)
	mu, sigma = 125, 25 # mean and standard deviation
	vect = None
	if mode == 1:
		#sport
		vect = np.random.normal(mu, sigma, 30)
	else:
		#rest
		vect = 8*np.random.gamma(shape, scaleRest, 30)+55
	i = 0
	while time.time() < t_end:
		myHeartSensor.publish(vect[i],mode)
		i = i+1
		time.sleep(5)
	
	myHeartSensor.client.stop()