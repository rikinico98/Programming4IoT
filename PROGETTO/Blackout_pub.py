#Blackout sensor simulator


from MyMQTT import *
import threading
import json
import time
import random
import requests


class MyThread(threading.Thread):

    def __init__(self, threadID, device, failure):
        threading.Thread.__init__(self)
        #Setup thread
        self.threadID = threadID
        self.device = device
        self.failure = failure

    def run(self):
        while True:
            u = random.uniform(0,1)
            if u > self.failure:
                # everything works!
                self.device.publish()
                time.sleep(0.5)
            else:
                # simulation of failure (failure holds for some time untill resolution of the problem)
                # stop sending MQTT messages
                time.sleep(random.uniform(2,10))


class blackoutSensor():

	def __init__(self, deviceID, roomID):
	    self.deviceID = deviceID
	    self.roomID = roomID
	    r_broker = requests.get(f'http://127.0.0.1:8080/catalog/msg_broker')
	    j_broker = json.dumps(r_broker.json(),indent=4)
	    d_broker = json.loads(j_broker)
	    self.broker = d_broker["msgBroker"]
	    r_port = requests.get(f'http://127.0.0.1:8080/catalog/port')
	    j_port = json.dumps(r_port.json(),indent=4)
	    d_port = json.loads(j_port)
	    self.port = d_port["port"]
	    self.device = MyMQTT(self.deviceID, self.broker, self.port, None)
	    r_topic = requests.get(f'http://127.0.0.1:8080/catalog/{self.roomID}/{self.deviceID}/topic')
	    j_topic = json.dumps(r_topic.json(),indent=4)
	    d_topic = json.loads(j_topic)
	    self.topic = d_topic["topic"] #Note: topic is a list
	    self.__message = {"bn": self.deviceID, "e": [{"n": "blackout detector", "u": "bool", "t": None, "v": 1}]}
	
	def start(self):
	    self.device.start()

	def stop(self):
	    self.device.stop()

	def publish(self):
	    message=self.__message
	    message["t"] = str(time.time())
	    for topic in self.topic:
	        self.device.myPublish(topic, message)


if __name__ == "__main__":

    # Take deviceID and roomID from a file with all the blackout sensors in the magazine.
	# The field "failure"  define the probability of "failure" (to simulate blackout situations).
	try:
	    devices = json.load(open("DevicesBlackout.json"))
	except:
	    print("File \"DevicesBlackout.json\" is not correct or present")
	devices = devices["devices"]
	myDevicesList = []
	failure = []

	for device in devices:
	    devID = device["deviceID"]
	    roomID = device["roomID"]
	    myDevicesList.append(blackoutSensor(devID,roomID))
	    failure.append(device["failure"])

	for device in myDevicesList:
	    device.start()

	devices_threads = []
	for i,device in enumerate(myDevicesList):
	    devices_threads.append(MyThread(i, device, failure[i]))

	for device in devices_threads:
	    device.start()
	
	for device in myDevicesList:
	    device.stop()