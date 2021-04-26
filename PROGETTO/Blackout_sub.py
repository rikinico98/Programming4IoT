#BLACKOUT SENSOR
# SUBSCRIBER DI sensore di BLACKOUT

# Receives messages from blackout sensor
# Rise telegram alarms if blackout occurs


from MyMQTT import *
import threading
import json
import time
import requests

class MyThread(threading.Thread):

    def __init__(self, threadID, device,URL):
        
        threading.Thread.__init__(self)
    
        #Setup thread
        self.threadID = threadID
        self.device = device
        self.iterate = True
        self.URL=URL
        self.__msg_bot1={"measure_type":"","ranges":[],"value":None,"Room":"","chatID":""}
        r_broker = requests.get(f'{self.URL}/catalog/MQTT_utilities') # richiesta al catalog di broker,port e general_topic
        if r_broker.status_code==200:
            j_broker = json.dumps(r_broker.json(),indent=4)
            d_broker = json.loads(j_broker) 
            self.broker = d_broker["MQTT_utilities"]["msgBroker"]
            self.port = d_broker["MQTT_utilities"]["port"]
            self.general_topic=d_broker["MQTT_utilities"]["mqttTopicGeneral"]
            self.dev = MyMQTT(self.threadID, self.broker, self.port, None)
        else:
            raise Exception(f"Request status code: {r_broker.status_code},Error occurred!")
    def run(self):
        while self.iterate:
            # If you have not received a message for more than a minute 
            currentTime = time.time()
            lastReceivedTime = json.loads(self.device.getLastReceivedTime())
            if lastReceivedTime["timestamp"] != None:
                if currentTime - float(lastReceivedTime["timestamp"]) > 8: # se per più di 8 secondi non ci sono dati del led allora c'è un blackout
                    print("ERRORE IN ARRRIVO!")
                    # Send periodically a Telegram alarm to the users
                    roomID = json.loads(self.device.getRoom())
                    deviceID = json.loads(self.device.getDeviceID())
                    room_ID=roomID["roomID"]
                    device_ID=deviceID["deviceID"]
                    msg_bot=self.__msg_bot1
                    users_dict1=requests.get(f'{self.URL}/catalog/{room_ID}/users')
                    if users_dict1.status_code==200:
                        users_dict2= json.dumps(users_dict1.json(),indent=4)
                        users_dict = json.loads(users_dict2)
                
                        for user in users_dict["user"]:
                            if 'M_' not in user:
                                chatID=self.FindChatID(user) # richiamo funzione per trovare i chatID legati all'user 
                                if chatID!=None:
                                    msg_bot["measure_type"]='blackout'
                                    msg_bot["ranges"] = None
                                    msg_bot["value"] = (currentTime-float(lastReceivedTime["timestamp"]))
                                    msg_bot["Room"] = roomID
                                    msg_bot["chatID"] = chatID
                                    self.dev.myPublish(f"{self.general_topic}/alarm/{room_ID}/{device_ID}",msg_bot)
                        time.sleep(5)
        
    def stop(self):
        self.iterate = False
    def FindChatID(self,userID):
        chat_dict1=requests.get(f'{self.URL}/catalog/{userID}/chatID') # richiesta delle chatID 
        if chat_dict1.status_code==200:
            chat_dict2= json.dumps(chat_dict1.json(),indent=4)
            chat_dict = json.loads(chat_dict2)
            chatID=chat_dict["chatID"]
        else:
            chatID=None
        return chatID

class blackoutReceiver():

    def __init__(self, deviceID, roomID,URL):
        self.deviceID = deviceID
        self.roomID = roomID
        self.URL=URL
        # Request broker from catalog
        r_broker = requests.get(f'{self.URL}/catalog/MQTT_utilities') #richiesta dI BROKER PORT E GENERAL TOPIC
        if r_broker.status_code==200:
            j_broker = json.dumps(r_broker.json(),indent=4)
            d_broker = json.loads(j_broker) 
            self.broker = d_broker["MQTT_utilities"]["msgBroker"]
            self.port = d_broker["MQTT_utilities"]["port"]
            self.general_topic=d_broker["MQTT_utilities"]["mqttTopicGeneral"]
            # Create the device
            self.device = MyMQTT(self.deviceID, self.broker, self.port, self)
        else:
            raise Exception(f"Request status code: {r_broker.status_code},Error occurred!")
        # Request topic from catalog
        r_topic = requests.get(f'{self.URL}/catalog/{self.roomID}/{self.deviceID}/topic') #richiesta del topic del dispositivo 
        if r_topic.status_code==200:
            j_topic = json.dumps(r_topic.json(),indent=4)
            d_topic = json.loads(j_topic)
            self.topic = d_topic["topic"] #Note: topic is a list
            # Define the last received timestamp
        else:
            raise Exception(f"Request status code: {r_topic.status_code},Error occurred!")
        self.lastReceivedTime = {"timestamp": None}
    
    def start(self):
        self.device.start()
        for topic in self.topic:
            self.device.mySubscribe(topic)
        self.device_thread = MyThread(self.deviceID, self,self.URL)
        self.device_thread.start()

    def stop(self):
        self.device_thread.stop()
        self.device.stop()

    def notify(self, topic, msg, qos):
        payload = json.loads(msg)
        print(f"Message received! Everything works correctly! Topic: {topic}, Measure: {payload['e'][0]['n']}, Value: {payload['e'][0]['v']}, Timestamp: {payload['e'][0]['t']} with Qos: {qos}")
        self.lastReceivedTime = {"timestamp": payload['e'][0]['t']}
    
    def getLastReceivedTime(self):
        return json.dumps(self.lastReceivedTime)

    def getRoom(self):
        return json.dumps({"roomID": self.roomID})

    def getDeviceID(self):
        return json.dumps({"deviceID": self.deviceID})



if __name__ == "__main__":
    myDevicesList = []
    current_rooms = []
    f = open('Settings.json',) # lettura dell'indirizzo del catalog dal file di Settings
    data = json.load(f)
    URL = data["catalogURL"]
    # Get all the rooms currently used
    r_rooms = requests.get(f'{URL}/catalog/rooms')
    if r_rooms.status_code == 200:
        j_rooms = json.dumps(r_rooms.json(),indent=4)
        d_rooms = json.loads(j_rooms)
        current_rooms_list = d_rooms["roomList"] #Note: rooms is a list
        for room in current_rooms_list:
            current_rooms.append(room["roomID"])
        
        # For all the rooms take all the blackout devices
        for room in current_rooms:
            r_devices = requests.get(f'{URL}/catalog/{room}/measure_type/blackout')
            if r_devices.status_code == 200:
                j_devices = json.dumps(r_devices.json(),indent=4)
                d_devices = json.loads(j_devices)
                devices = d_devices["foundIDs"] #Note: devices is a list
                # Create a thread for each device
                for device in devices:
                    myDevicesList.append(blackoutReceiver(device, room,URL))
                    print(f"New device added: {device}")

        for device in myDevicesList:
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
                r_devices = requests.get(f'{URL}/catalog/{room}/measure_type/blackout')
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
                        myDevicesList.append(blackoutReceiver(device, room,URL))
                        myDevicesList[-1].start()
                        print(f"New device added: {device}")

            # Find all the devices to add from new rooms
            # Rooms that must be added
            rooms_to_add = list(set(update_rooms) - set(current_rooms))
            # Add that rooms to current rooms
            current_rooms = current_rooms + rooms_to_add
            # Add all the devices within the rooms to add
            for room in rooms_to_add:
                r_devices = requests.get(f'{URL}/catalog/{room}/measure_type/blackout')
                if r_devices.status_code == 200:
                    j_devices = json.dumps(r_devices.json(),indent=4)
                    d_devices = json.loads(j_devices)
                    devices = d_devices["foundIDs"] #Note: devices is a list
                    # Create a thread for each device
                    for device in devices:
                        myDevicesList.append(blackoutReceiver(device, room,URL))
                        myDevicesList[-1].start()
                        print(f"New device added: {device}")