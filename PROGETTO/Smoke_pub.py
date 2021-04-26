#SMOKE SIMULATOR
#PUBLISHER DEL SENSORE DI SMOKE

from MyMQTT import *
import threading
import json
import time
import random
import requests
import math
import numpy as np

class MyThread(threading.Thread):

    def __init__(self, threadID, device, failure,URL,roomID):
        threading.Thread.__init__(self)
        #Setup thread
        self.threadID = threadID
        self.device = device
        self.iterate = True
        self.failure = failure
        self.URL=URL
        self.roomID=roomID
        ranges_dict1=requests.get(f'{self.URL}/catalog/{self.roomID}/ranges')  # richiesat dei range di normalità 
        if ranges_dict1.status_code==200:
            ranges_dict2= json.dumps(ranges_dict1.json(),indent=4)
            ranges_dict = json.loads(ranges_dict2)
            self.alert_val=ranges_dict["ranges"]["Smoke"]
        else:
            raise Exception(f"Request status code: {ranges_dict1.status_code},Error occurred!")
        self.loc1=random.uniform(200,int(self.alert_val[0])) # impostando una soglia anomala al di sopra del 300 in questo modo otteniamo una distribuzione
        # tra 200 ppm  minimo valore acquisibile da un tipico sensore e la soglia impostata per il sensore 

    def run(self):
        while self.iterate:
            # Concentration scope: from 200ppm to 10000ppm
            # When the gas concentration is high enough, the sensor usually outputs value greater than 300.
            p = random.uniform(0,1)
            time.sleep(120)
            if p > self.failure:
                #u = random.uniform(200,300)
                loc, scale = self.loc1, 0.1
                a= np.random.logistic(loc, scale, 10000)
                u = random.choice(a)
            else:
                u = random.uniform(int(self.alert_val[0]),10000) # tutti i valori al di sopra della soglia del sensore  e 10000 valore massimo acquisibile 
            if u < 400:
                # Everything works!
                self.device.publish(u)
               
            else:
                # Simulation of failure (failure holds for some time untill resolution of the problem)
                # Keep sending the wrong result to simulate the time needed to solve the problem
                time_to_solve = math.ceil(random.uniform(5,15)) 
                for it in range(time_to_solve):
                    self.device.publish(u)
                    time.sleep(120)
                    
    def stop(self):
        self.iterate = False


class smokeSensor():

    def __init__(self, ID, deviceID, roomID, failure,URL):
        self.ID = ID
        self.deviceID = deviceID
        self.roomID = roomID
        self.failure = failure
        self.URL=URL
        # Request broker from catalog
        r_broker = requests.get(f'{self.URL}/catalog/MQTT_utilities') # richiesta di porta,broker 
        try:
            j_broker = json.dumps(r_broker.json(),indent=4)
            d_broker = json.loads(j_broker)
            self.broker = d_broker["MQTT_utilities"]["msgBroker"]
            self.port = d_broker["MQTT_utilities"]["port"]
            # Create the device
            self.device = MyMQTT(self.ID, self.broker, self.port, None)
        except:
            raise Exception(f"{r_devices.status_code},Error occurred!")
        # Request topic from catalog
        r_topic = requests.get(f'{self.URL}/catalog/{self.roomID}/{self.deviceID}/topic') #richiesta del topic del singolo dispostivo 
        try: 
            j_topic = json.dumps(r_topic.json(),indent=4)
            d_topic = json.loads(j_topic)
            self.topic = d_topic["topic"] #Note: topic is a list
            # Define standard message to send
            self.__message = {"bn": self.deviceID, "e": [{"n": "smoke detector", "u": "ppm", "t": None, "v": None}]}
        except:
            raise Exception(f"{r_topic.status_code},Error occurred!")
    
    def start(self):
        self.device.start()
        self.device_thread = MyThread(self.ID, self, self.failure,self.URL,self.roomID)
        self.device_thread.start()

    def stop(self):
        self.device_thread.stop()
        self.device.stop()

    def publish(self, value):
        message=self.__message
        # Add timestamp
        message["e"][0]["t"] = str(time.time())
        # Add value
        message["e"][0]["v"] = value
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
    f = open('Settings.json')
    data = json.load(f)
    URL = data["catalogURL"]
    # Get all the rooms currently used
    r_rooms = requests.get(f' {URL}/catalog/rooms') #rihiesta delle stanze 
    # Get all the rooms currently used
    if r_rooms.status_code == 200:
        j_rooms = json.dumps(r_rooms.json(),indent=4)
        d_rooms = json.loads(j_rooms)
        current_rooms_list = d_rooms["roomList"] #Note: rooms is a list
        for room in current_rooms_list:
            current_rooms.append(room["roomID"])    
        # For all the rooms take all the smoke devices
        for room in current_rooms:
            r_devices = requests.get(f'{URL}/catalog/{room}/measure_type/smoke') # richiesta dei dispositivi di smoke per ciascuna stanza 
            if r_devices.status_code == 200:
                j_devices = json.dumps(r_devices.json(),indent=4)
                d_devices = json.loads(j_devices)
                devices = d_devices["foundIDs"] #Note: devices is a list
                # Create a thread for each device
                for device in devices:
                    myDevicesList.append(smokeSensor(device+"_pub", device, room, failure_probability,URL))
                    print(f"New device added: {device}")

        for device in myDevicesList:
            time.sleep(20)
            device.start()

    # Keep updating the previous devices
    while True:
        time.sleep(5)
        # Get all the updated rooms
        update_rooms = []
        r_rooms = requests.get(f'{URL}/catalog/rooms')
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
            for room in current_rooms:
                r_devices = requests.get(f'{URL}/catalog/{room}/measure_type/smoke')
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
                        myDevicesList.append(smokeSensor(device+"_pub", device, room, failure_probability,URL))
                        myDevicesList[-1].start()
                        print(f"New device added: {device}")

            # Find all the devices to add from new rooms
            # Rooms that must be added
            rooms_to_add = list(set(update_rooms) - set(current_rooms))
            # Add that rooms to current rooms
            current_rooms = current_rooms + rooms_to_add
            # Add all the devices within the rooms to add
            for room in rooms_to_add:
                r_devices = requests.get(f'{URL}/catalog/{room}/measure_type/smoke')
                if r_devices.status_code == 200:
                    j_devices = json.dumps(r_devices.json(),indent=4)
                    d_devices = json.loads(j_devices)
                    devices = d_devices["foundIDs"] #Note: devices is a list
                    # Create a thread for each device
                    for device in devices:
                        myDevicesList.append(smokeSensor(device+"_pub", device, room, failure_probability,URL))
                        myDevicesList[-1].start()
                        print(f"New device added: {device}")