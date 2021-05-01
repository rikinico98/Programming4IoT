#SMOKE SIMULATOR
#SUBSCRIBER DEL SENSORE DI SMOKE
# Receives messages from smoke sensor
# Rise telegram alarms if smoke detected is too high 

from MyMQTT import *
import threading
import json
import time
import requests

class smokeReceiver():

    def __init__(self, deviceID, roomID,URL):
        self.deviceID = deviceID
        self.roomID = roomID
        self.URL=URL
        # Request broker from catalog
        r_broker = requests.get(f'{self.URL}/catalog/MQTT_utilities')# richiesta al catalog di broker,porta e topic generale 
        if r_broker.status_code==200:
            j_broker = json.dumps(r_broker.json(),indent=4)
            d_broker = json.loads(j_broker) 
            self.broker = d_broker["MQTT_utilities"]["msgBroker"]
            self.port = d_broker["MQTT_utilities"]["port"]
            self.general_topic=d_broker["MQTT_utilities"]["mqttTopicGeneral"]
            field = requests.get(f'{self.URL}/catalog/{self.roomID}/{self.deviceID}/get_field') #richiesta dei campi di ThingSpeak 
            if field.status_code==200:
                field_field1 = json.dumps(field.json(), indent = 4)
                self.field_field = json.loads(field_field1)
            else: 
                self.field_field=[]
        # Create the device
            self.device = MyMQTT(self.deviceID, self.broker, self.port, self)
        # Request topic from catalog
        else:
            raise Exception(f"Request status code: {r_broker.status_code},Error occurred!")
        
        r_topic = requests.get(f'{self.URL}/catalog/{self.roomID}/{self.deviceID}/topic') #richiesta dei topic del device 
        if r_topic.status_code==200:
            j_topic = json.dumps(r_topic.json(),indent=4)
            d_topic = json.loads(j_topic)
            self.topic = d_topic["topic"] #Note: topic is a list
        else:
            raise Exception(f"Request status code: {r_topic.status_code},Error occurred!")
        self.__message1={"TS_api":"","ThingSpeak_field": "", "v": None}
        self.__msg_bot1={"measure_type":"","ranges":[],"value":None,"Room":"","chatID":""}
        print(f'Room ID: {self.roomID}, Device ID:{self.deviceID}')

    def FindChatID(self,userID):
        chat_dict1=requests.get(f'{self.URL}/catalog/{userID}/chatID') #richiesta dei chatID connessi alla stanza
        if chat_dict1.status_code==200:
            chat_dict2= json.dumps(chat_dict1.json(),indent=4)
            chat_dict = json.loads(chat_dict2)
            print(chat_dict)
            chatID=chat_dict["chatID"]
        else: 
            chatID=None
        return chatID
    
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
        r_TS = requests.get(f'{self.URL}/catalog/{self.roomID}/TS_utilities') # richiesta delle APIkey di ThingSpeak per scrivere i dati nel canale 
        if r_TS.status_code==200 and len(self.field_field["field"])==1:
            j_TS = json.dumps(r_TS.json(),indent=4)
            d_TS = json.loads(j_TS)
            TS=d_TS["ThingSpeak"]
            message["TS_api"]=TS["api_key_write"]
            message["ThingSpeak_field"]=self.field_field["field"][0]
            message["v"]=smoke_value
            topic_TS = requests.get(f'{self.URL}/catalog/Thingspeak_API') 
            if topic_TS.status_code==200:
                topic_TS1 = json.dumps(topic_TS.json(),indent=4)
                topic_TS = json.loads(topic_TS1)
                TS_topic=topic_TS["Thingspeak_API"]["mqttTopicThingspeak"]
                if TS_topic!='':
                    self.device.myPublish(TS_topic,message)
            
        ranges_dict1=requests.get(f'{self.URL}/catalog/{self.roomID}/ranges')  # richiesat dei range di normalità 
        if ranges_dict1.status_code==200:
            ranges_dict2= json.dumps(ranges_dict1.json(),indent=4)
            ranges_dict = json.loads(ranges_dict2)
            alert_val=ranges_dict["ranges"]["Smoke"]
        else:
            raise Exception(f"Request status code: {ranges_dict1.status_code},Error occurred!")
        
        if int(smoke_value)>= int(alert_val[0]): # se si è in codizioni sopra la soglia critica 
            msg_bot=self.__msg_bot1
            users_dict1=requests.get(f'{self.URL}/catalog/{self.roomID}/users') # richiesta degli utenti 
            if users_dict1.status_code==200:
                users_dict2= json.dumps(users_dict1.json(),indent=4)
                users_dict = json.loads(users_dict2)
                for user in users_dict["user"]:
                    if 'M_' not in user:
                        chatID=self.FindChatID(user) # richiamo alla funzione per trovare i chatID
                        if chatID!=None:
                            msg_bot["measure_type"]='smoke'
                            msg_bot["ranges"] = alert_val
                            msg_bot["value"] = smoke_value
                            msg_bot["Room"] = self.roomID
                            msg_bot["chatID"] = chatID
                            self.device.myPublish(f"BOT/{self.general_topic}/alarm/{self.roomID}/{self.deviceID}",msg_bot)
            

    def getRoom(self):
        return json.dumps({"roomID": self.roomID})
    
    def getDeviceID(self):
        return json.dumps({"deviceID": self.deviceID})



if __name__ == "__main__":
    myDevicesList = []
    current_rooms = []
    myDevicesList = []
    current_rooms = []
    f = open('Settings.json') 
    data = json.load(f)
    URL = data["catalogURL"]
    # Get all the rooms currently used
    r_rooms = requests.get(f' {URL}/catalog/rooms') 
    if r_rooms.status_code == 200:
        j_rooms = json.dumps(r_rooms.json(),indent=4)
        d_rooms = json.loads(j_rooms)
        current_rooms_list = d_rooms["roomList"] #Note: rooms is a list
        for room in current_rooms_list:
            current_rooms.append(room["roomID"])
    
        # For all the rooms take all the smoke devices
        for room in current_rooms:
            r_devices = requests.get(f'{URL}/catalog/{room}/measure_type/smoke')
            if r_devices.status_code == 200:
                j_devices = json.dumps(r_devices.json(),indent=4)
                d_devices = json.loads(j_devices)
                devices = d_devices["foundIDs"] #Note: devices is a list
                # Create a thread for each device
                for device in devices:
                    myDevicesList.append(smokeReceiver(device,room,URL))
                    print(f"New device added: {device}")
            else:
                raise Exception(f"{r_devices.status_code},Error occurred!")

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
                        myDevicesList.append(smokeReceiver(device,room,URL))
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
                        myDevicesList.append(smokeReceiver(device,room,URL))
                        myDevicesList[-1].start()
                        print(f"New device added: {device}")