# Receives messages from blackout sensor
# Rise telegram alarms if blackout occurs


from MyMQTT import *
import threading
import json
import time
import requests
import telepot
from telepot.loop import MessageLoop


# class MyBot():

#     def __init__(self, token):
#         self.tokenBot = token
#         self.bot = telepot.Bot(self.tokenBot)
#         MessageLoop(self.bot, {"chat": self.on_chat_message}).run_as_thread()
    
#     def on_chat_message(self,msg):
#         # Get chat ID
#         content_type, chat_type, chat_ID = telepot.glance(msg)
#         self.chat_ID = chat_ID

#     def SendAlarm(self, room, device_id):
#         # Publish alarm message when blackout is detected
#         self.bot.sendMessage(self.chat_ID, text = f"ALARM: blackout in room {room}. Check device {device_id}")


class MyThread(threading.Thread):

    def __init__(self, threadID, device):
        threading.Thread.__init__(self)
        #Setup thread
        self.threadID = threadID
        self.device = device
        self.iterate = True
        self.__msg_bot1={"measure_type":"","ranges":[],"value":None,"Room":"","chatID":""}
        r_broker = requests.get(f'http://127.0.0.1:8070/catalog/MQTT_utilities')
        print(r_broker)
        j_broker = json.dumps(r_broker.json(),indent=4)
        d_broker = json.loads(j_broker) 
        self.broker = d_broker["MQTT_utilities"]["msgBroker"]
        self.port = d_broker["MQTT_utilities"]["port"]
        self.general_topic=d_broker["MQTT_utilities"]["mqttTopicGeneral"]
        self.dev = MyMQTT(self.threadID, self.broker, self.port, None)
    def run(self):
        while self.iterate:
            # If you have not received a message for more than a minute 
            currentTime = time.time()
            lastReceivedTime = json.loads(self.device.getLastReceivedTime())
            if lastReceivedTime["timestamp"] != None:
                if currentTime - float(lastReceivedTime["timestamp"]) > 8:
                    print("ERRORE IN ARRRIVO!")
                    # Send periodically a Telegram alarm to the users
                    roomID = json.loads(self.device.getRoom())
                    deviceID = json.loads(self.device.getDeviceID())
                    room_ID=roomID["roomID"]
                    device_ID=deviceID["deviceID"]
                    #self.botTelegram.SendAlarm(roomID["roomID"], deviceID["deviceID"])
                    msg_bot=self.__msg_bot1
                    print(roomID["roomID"])
                   
                    print(f'http://127.0.0.1:8070/catalog/{room_ID}/users')
                    users_dict1=requests.get(f'http://127.0.0.1:8070/catalog/{room_ID}/users')
                    users_dict2= json.dumps(users_dict1.json(),indent=4)
                    users_dict = json.loads(users_dict2)
                    print(users_dict1)
                    for user in users_dict["user"]:
                        print(user)
                        if 'M_' not in user:
                            chatID=self.__FindChatID(user)
                            msg_bot["measure_type"]='blackout'
                            msg_bot["ranges"] = None
                            msg_bot["value"] = (currentTime-float(lastReceivedTime["timestamp"]))
                            msg_bot["Room"] = roomID
                            msg_bot["chatID"] = chatID
                            self.dev.myPublish(f"{self.general_topic}/alarm/{room_ID}/{device_ID}",msg_bot)
                    time.sleep(5)
    
    def stop(self):
        self.iterate = False
    def __FindChatID(self,userID):
        print(userID)
        chat_dict1=requests.get(f'http://127.0.0.1:8070/catalog/{userID}/chatID')
        chat_dict2= json.dumps(chat_dict1.json(),indent=4)
        chat_dict = json.loads(chat_dict2)
        print(chat_dict)
        chatID=chat_dict["chatID"]
        return chatID

class blackoutReceiver():

    def __init__(self, deviceID, roomID):
        self.deviceID = deviceID
        self.roomID = roomID
        # Request broker from catalog
        r_broker = requests.get(f'http://127.0.0.1:8070/catalog/MQTT_utilities')
        print(r_broker)
        j_broker = json.dumps(r_broker.json(),indent=4)
        d_broker = json.loads(j_broker) 
        self.broker = d_broker["MQTT_utilities"]["msgBroker"]
        self.port = d_broker["MQTT_utilities"]["port"]
        self.general_topic=d_broker["MQTT_utilities"]["mqttTopicGeneral"]
        # Create the device
        self.device = MyMQTT(self.deviceID, self.broker, self.port, self)
        # Request topic from catalog
        r_topic = requests.get(f'http://127.0.0.1:8070/catalog/{self.roomID}/{self.deviceID}/topic')
        j_topic = json.dumps(r_topic.json(),indent=4)
        d_topic = json.loads(j_topic)
        self.topic = d_topic["topic"] #Note: topic is a list
        # Define the last received timestamp
        self.lastReceivedTime = {"timestamp": None}
    
    def start(self):
        self.device.start()
        for topic in self.topic:
            self.device.mySubscribe(topic)
        self.device_thread = MyThread(self.deviceID, self,)
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
                    myDevicesList.append(blackoutReceiver(device, room))
                    print(f"New device added: {device}")

        for device in myDevicesList:
            device.start()

    # Keep updating the previous devices
    while True:
        time.sleep(5)
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
                        myDevicesList.append(blackoutReceiver(device, room))
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
                        myDevicesList.append(blackoutReceiver(device, room))
                        myDevicesList[-1].start()
                        print(f"New device added: {device}")