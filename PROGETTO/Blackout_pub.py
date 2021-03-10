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
        self.iterate = True

    def run(self):
        while self.iterate:
            u = random.uniform(0,1)
            if u > self.failure:
                # Everything works!
                self.device.publish()
                time.sleep(5)
            else:
                # Simulation of failure (failure holds for some time untill resolution of the problem)
                # Stop sending MQTT messages
                time.sleep(random.uniform(10,40))
	
    def stop(self):
    	self.iterate = False


class blackoutSensor():

	def __init__(self, ID, deviceID, roomID, failure):
	    self.ID = ID
	    self.deviceID = deviceID
	    self.roomID = roomID
	    self.failure = failure
		# Request broker from catalog
	    r_broker = requests.get(f'http://127.0.0.1:8070/catalog/msg_broker')
	    j_broker = json.dumps(r_broker.json(),indent=4)
	    d_broker = json.loads(j_broker)
	    self.broker = d_broker["msgBroker"]
		# Request port from catalog
	    #r_port = requests.get(f'http://127.0.0.1:8070/catalog/port')
	    #j_port = json.dumps(r_port.json(),indent=4)
	    #d_port = json.loads(j_port)
	    #self.port = d_port["port"]
	    self.port = 1883
		# Create the device
	    self.device = MyMQTT(self.ID, self.broker, self.port, None)
		# Request topic from catalog
	    r_topic = requests.get(f'http://127.0.0.1:8070/catalog/{self.roomID}/{self.deviceID}/topic')
	    j_topic = json.dumps(r_topic.json(),indent=4)
	    d_topic = json.loads(j_topic)
	    self.topic = d_topic["topic"] #Note: topic is a list
		# Define standard message to send
	    self.__message = {"bn": self.deviceID, "e": [{"n": "blackout detector", "u": "bool", "t": None, "v": 1}]}
	
	def start(self):
		self.device.start()
		self.device_thread = MyThread(self.ID, self, self.failure)
		self.device_thread.start()

	def stop(self):
	    self.device_thread.stop()
	    self.device.stop()

	def publish(self):
	    message=self.__message
		# Add timestamp
	    message["e"][0]["t"] = str(time.time())
		# Publish to all the topics
	    for topic in self.topic:
	        self.device.myPublish(topic, message)
	
	def getRoom(self):
		return json.dumps({"roomID": self.roomID})
	
	def getDeviceID(self):
		return json.dumps({"deviceID": self.deviceID})



if __name__ == "__main__":

	# To simulate failure of the real sensor
	failure_probability = -1
	while failure_probability < 0 or failure_probability > 1:
		failure_probability = float(input("Insert the failure probability to simulate\nNote: it must be a number in [0,1]\n"))

	myDevicesList = []
	current_rooms = []
	# Get all the rooms currently used
	r_rooms = requests.get(f'http://127.0.0.1:8070/catalog/rooms')
	if r_rooms.status_code == 200:
		j_rooms = json.dumps(r_rooms.json(),indent=4)
		d_rooms = json.loads(j_rooms)
		current_rooms_list = d_rooms["roomList"] #Note: rooms is a list
		for room in current_rooms_list:
			current_rooms.append(room["roomID"])
		
		# For all the rooms take all the blackout devices
		for room in current_rooms:
			r_devices = requests.get(f'http://127.0.0.1:8070/catalog/{room}/measure_type/blackout')
			if r_devices.status_code == 200:
				j_devices = json.dumps(r_devices.json(),indent=4)
				d_devices = json.loads(j_devices)
				devices = d_devices["foundIDs"] #Note: devices is a list
				# Create a thread for each device
				for device in devices:
					myDevicesList.append(blackoutSensor(device+"_pub", device, room, failure_probability))
					print(f"New device added: {device}")

		for device in myDevicesList:
			device.start()

	# Keep updating the previous devices
	while True:
		time.sleep(10)
		# Get all the updated rooms
		update_rooms = []
		r_rooms = requests.get(f'http://127.0.0.1:8070/catalog/rooms')
		if r_rooms.status_code == 200:
			j_rooms = json.dumps(r_rooms.json(),indent=4)
			d_rooms = json.loads(j_rooms)
			update_rooms_list = d_rooms["roomList"] #Note: update_rooms is a list
			for room in update_rooms_list:
				update_rooms.append(room["roomID"])

			# Find all devices to delete
			# Rooms that must be deleted
			rooms_to_delete = list(set(current_rooms) - set(update_rooms))
			# Delete that rooms form current rooms
			current_rooms = list(set(current_rooms) - set(rooms_to_delete))
			# Delete all the devices within the rooms to remove
			device_to_delete = []
			for room in rooms_to_delete:
				for device in myDevicesList:
					device_room = json.loads(device.getRoom())
					if room == device_room["roomID"]:
						device.stop()
						device_to_delete.append(json.loads(device.getDeviceID())["deviceID"])
			for del_device in device_to_delete:
				for i, device in enumerate(myDevicesList):
					if del_device == json.loads(device.getDeviceID())["deviceID"]:
						del myDevicesList[i]

			# Check for changes in the remaining rooms
			device_to_delete = []
			for room in current_rooms:
				r_devices = requests.get(f'http://127.0.0.1:8070/catalog/{room}/measure_type/blackout')
				if r_devices.status_code == 200:
					j_devices = json.dumps(r_devices.json(),indent=4)
					d_devices = json.loads(j_devices)
					devices = d_devices["foundIDs"] #Note: devices is a list
					device_in_room = []
					for device in myDevicesList:
						device_room = json.loads(device.getRoom())
						if room == device_room["roomID"]:
							device_id = json.loads(device.getDeviceID())
							device_in_room.append(device_id["deviceID"])
					# Delete old devices
					old_devices = list(set(device_in_room) - set(devices))
					device_in_room = list(set(device_in_room) - set(old_devices))
					for old_device in old_devices:
						for device in myDevicesList:
							device_id = json.loads(device.getDeviceID())
							if old_device == device_id["deviceID"]:
								device.stop()
								device_to_delete.append(json.loads(device.getDeviceID())["deviceID"])
					for del_device in device_to_delete:
						for i, device in enumerate(myDevicesList):
							if del_device == json.loads(device.getDeviceID())["deviceID"]:
								del myDevicesList[i]
					# Add new devices
					missing_devices = list(set(devices) - set(device_in_room))
					for device in missing_devices:
						myDevicesList.append(blackoutSensor(device+"_pub", device, room, failure_probability))
						myDevicesList[-1].start()
						print(f"New device added: {device}")

			# Find all the devices to add from new rooms
			# Rooms that must be added
			rooms_to_add = list(set(update_rooms) - set(current_rooms))
			# Add that rooms to current rooms
			current_rooms = current_rooms + rooms_to_add
			# Add all the devices within the rooms to add
			for room in rooms_to_add:
				r_devices = requests.get(f'http://127.0.0.1:8070/catalog/{room}/measure_type/blackout')
				if r_devices.status_code == 200:
					j_devices = json.dumps(r_devices.json(),indent=4)
					d_devices = json.loads(j_devices)
					devices = d_devices["foundIDs"] #Note: devices is a list
					# Create a thread for each device
					for device in devices:
						myDevicesList.append(blackoutSensor(device+"_pub", device, room, failure_probability))
						myDevicesList[-1].start()
						print(f"New device added: {device}")