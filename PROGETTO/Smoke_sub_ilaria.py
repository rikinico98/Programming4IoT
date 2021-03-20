# Receives messages from smoke sensor
# Rise telegram alarms if smoke detected is too high 


from MyMQTT import *
import threading
import json
import time
import requests
# import telepot
# from telepot.loop import MessageLoop


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
#         # Publish alarm message when smoke is detected
        # self.bot.sendMessage(self.chat_ID, text = f"ALARM: smoke in room {room}. Check device {device_id}")

class smokeReceiver():

    def __init__(self, deviceID, roomID):
        self.deviceID = deviceID
        self.roomID = roomID
        self.apikey = '4O6ZLEXF1XAQ933O' #va letto dal Catalog 
        self.baseURL = f"https://api.thingspeak.com/update?api_key={self.apikey}" 
        # Request broker from catalog
        r_broker = requests.get(f'http://127.0.0.1:8070/catalog/msg_broker')
        j_broker = json.dumps(r_broker.json(),indent=4)
        d_broker = json.loads(j_broker)
        self.broker = d_broker["msgBroker"]
        # Request port from catalog
        r_port = requests.get(f'http://127.0.0.1:8070/catalog/port')
        j_port = json.dumps(r_port.json(),indent=4)
        d_port = json.loads(j_port)
        self.port = d_port["port"]
        # Create the device
        self.device = MyMQTT(self.deviceID, self.broker, self.port, self)
        # Request topic from catalog
        r_topic = requests.get(f'http://127.0.0.1:8070/catalog/{self.roomID}/{self.deviceID}/topic')
        
        j_topic = json.dumps(r_topic.json(),indent=4)
        d_topic = json.loads(j_topic)
        self.topic = d_topic["topic"] #Note: topic is a list
        # self.botTelegram = botTelegram
        print(self.topic)
        self.__message1={"TS_api":"","ThingSpeak_field": "", "v": None}
    
    def start(self):
        self.device.start()
        for topic in self.topic:
            self.device.mySubscribe(topic)

    def stop(self):
        self.device.stop()

    def notify(self,topic,msg,qos):
        payload = json.loads(msg)
        print(f"Message received! Everything works correctly! Topic: {topic}, Measure: {payload['e'][0]['n']}, Value: {payload['e'][0]['v']}, Timestamp: {payload['e'][0]['t']} with QoS: {qos}")
        smoke_value = payload['e'][0]['v']
        time.sleep(5)
        message=self.__message1
        r_TS = requests.get(f'http://127.0.0.1:8070/catalog/{self.roomID}/TS_utilities')
        j_TS = json.dumps(r_TS.json(),indent=4)
        d_TS = json.loads(j_TS)
        TS=d_TS["ThingSpeak"]
        print(d_TS)
        message["TS_api"]=TS["api_key_write"]
        message["ThingSpeak_field"]="field3"
        message["v"]=smoke_value
        self.device.myPublish("ThingSpeak/channel/allsensor",message)
        ranges_dict1=requests.get(f'http://127.0.0.1:8070/catalog/{self.roomID}/ranges') 
        ranges_dict2= json.dumps(ranges_dict1.json(),indent=4)
        ranges_dict = json.loads(ranges_dict2)
        print(ranges_dict)
        alert_val=ranges_dict["ranges"]["Smoke"]
        # print(alert_val)
            # r = requests.get(self.baseURL+f'&field2={smoke_value}') 
        # If the value of the message received is out of the normal range
        # When the gas concentration is high enough, the sensor usually outputs value greater than 300.
        if ((int(smoke_value)>= int(alert_val[1])) or (int(smoke_value) <= int(alert_val[0]))):
            print("SCAPPPAAAAAA")
            # capire con riccardo come inviare a telegram
        # if smoke_value >= 300:
        #     # Send a Telegram alarm to the users
        #     self.botTelegram.SendAlarm(self.roomID, self.deviceID)

    def getRoom(self):
        return json.dumps({"roomID": self.roomID})
    
    def getDeviceID(self):
        return json.dumps({"deviceID": self.deviceID})



if __name__ == "__main__":

    # botTelegram = MyBot("1669000654:AAFKE-wI5v4Lm--42edkv9T8PS6ruMneybE")

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
    
        # For all the rooms take all the smoke devices
        for room in current_rooms:
            r_devices = requests.get(f'http://127.0.0.1:8070/catalog/{room}/measure_type/smoke')
            if r_devices.status_code == 200:
                j_devices = json.dumps(r_devices.json(),indent=4)
                d_devices = json.loads(j_devices)
                devices = d_devices["foundIDs"] #Note: devices is a list
                # Create a thread for each device
                for device in devices:
                    myDevicesList.append(smokeReceiver(device,room))
                    # myDevicesList.append(smokeReceiver(device,room,botTelegram))
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
                r_devices = requests.get(f'http://127.0.0.1:8070/catalog/{room}/measure_type/smoke')
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
                        myDevicesList.append(smokeReceiver(device,room,botTelegram))
                        myDevicesList[-1].start()
                        print(f"New device added: {device}")

            # Find all the devices to add from new rooms
            # Rooms that must be added
            rooms_to_add = list(set(update_rooms) - set(current_rooms))
            # Add that rooms to current rooms
            current_rooms = current_rooms + rooms_to_add
            # Add all the devices within the rooms to add
            for room in rooms_to_add:
                r_devices = requests.get(f'http://127.0.0.1:8070/catalog/{room}/measure_type/smoke')
                if r_devices.status_code == 200:
                    j_devices = json.dumps(r_devices.json(),indent=4)
                    d_devices = json.loads(j_devices)
                    devices = d_devices["foundIDs"] #Note: devices is a list
                    # Create a thread for each device
                    for device in devices:
                        myDevicesList.append(smokeReceiver(device,room,botTelegram))
                        myDevicesList[-1].start()
                        print(f"New device added: {device}")