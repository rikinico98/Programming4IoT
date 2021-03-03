# Receives messages from blackout sensor
# Rise telegram alarms if blackout occurs


from MyMQTT import *
import threading
import json
import time
import requests


class MyThread(threading.Thread):

    def __init__(self, threadID, device):
        threading.Thread.__init__(self)
        #Setup thread
        self.threadID = threadID
        self.device = device

    def run(self):
        while True:
            currentTime = time.time()
            lastReceivedTime = self.device.getLastReceivedTime()
            if lastReceivedTime["timestamp"] != None:
                if currentTime - lastReceivedTime["timestamp"] > 1:
                    # Messages no more received
                    # Rise telegram error
                    pass


class blackoutReceiver():

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
        self.lastReceivedTime = {"timestamp": None}
    
    def start(self):
        self.device.start()
        for topic in self.topic:
            self.device.mySubscribe(topic)

    def stop(self):
        self.device.stop()

    def notify(self,topic,msg):
        payload = json.loads(msg)
        print(f"Message received! Everything works correctly!\nTopic: {topic}\nMeasure: {payload['e'][0]['n']}\n\
            Value: {payload['e'][0]['v']}\nTimestamp: {payload['e'][0]['t']}\n")
        self.lastReceivedTime = {"timestamp": payload['e'][0]['t']}
    
    def getLastReceivedTime(self):
        return self.lastReceivedTime


if __name__=="__main__":

    # Take deviceID and roomID from a file with all the blackout sensors in the magazine.
	try:
	    devices = json.load(open("DevicesBlackout.json"))
	except:
	    print("File \"DevicesBlackout.json\" is not correct or present")
	devices = devices["devices"]
	myDevicesList = []
	
	for device in devices:
	    devID = device["deviceID"]
	    roomID = device["roomID"]
	    myDevicesList.append(blackoutReceiver(devID,roomID))
    
	for device in myDevicesList:
	    device.start()

	devices_threads = []
	for i,device in enumerate(myDevicesList):
	    devices_threads.append(MyThread(i, device))

	for device in devices_threads:
	    device.start()
	
	for device in myDevicesList:
	    device.stop()