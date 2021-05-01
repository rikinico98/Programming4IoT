#TEMP HUM SENSOR
# SUBSCRIBER DI TEMPERATURA E UMIDITA'
# Send to telegram alarms if smoke detected is too high 
from MyMQTT import *
import threading
import json
import time
import requests

class TEMPHUMReceiver():

    def __init__(self, deviceID, roomID,URL):
        self.URL=URL
        self.deviceID = deviceID
        self.roomID = roomID 
        r_broker = requests.get(f'{self.URL}/catalog/MQTT_utilities') ## ottengo broker e porta dal catalog 
        if r_broker.status_code==200:
            j_broker = json.dumps(r_broker.json(),indent=4)
            d_broker = json.loads(j_broker) 
            self.broker = d_broker["MQTT_utilities"]["msgBroker"]
            self.port = d_broker["MQTT_utilities"]["port"]
            self.Generaltopic=d_broker["MQTT_utilities"]["mqttTopicGeneral"]
            field = requests.get(f'{self.URL}/catalog/{self.roomID}/{self.deviceID}/get_field') # ottengo la lista dei campi di thingspeak
            if field.status_code==200:
                field_field1 = json.dumps(field.json(), indent = 4)
                self.field_field = json.loads(field_field1)
            else:
                self.field_field =[]
            # Create the device 
            self.device = MyMQTT(self.deviceID, self.broker, self.port, self)
            # Request topic from catalog
        else:
            raise Exception(f"Request status code: {r_broker.status_code},Error occurred!")
        r_topic = requests.get(f'{self.URL}/catalog/{self.roomID}/{self.deviceID}/topic') # ottengo il topic del device dal catalog
        if r_topic.status_code==200:
            j_topic = json.dumps(r_topic.json(),indent=4)
            d_topic = json.loads(j_topic)
            self.topic = d_topic["topic"] #Note: topic is a list
            self.__message1={"TS_api":"", "ThingSpeak_field": "", "v": None}
            self.__msg_bot1={"measure_type":"","ranges":[],"value":None,"Room":"","chatID":""}
        else:
            raise Exception(f"Request status code: {r_topic.status_code},Error occurred!")
        r_roomtype = requests.get(f'{self.URL}/catalog/{self.roomID}/assigned_product_type') # ottengo il tipo di stanza dal catalog
        if r_roomtype.status_code==200:
            j_roomtype = json.dumps(r_roomtype.json(),indent=4)
            d_roomtype = json.loads(j_roomtype)
            self.roomtype = d_roomtype["product_type"] #Note: topic is a list
            
        else:
            raise Exception(f"Request status code: {r_roomtype.status_code},Error occurred!")
        print(f'Room ID: {self.roomID}, Device ID:{self.deviceID}, Product type:{self.roomtype}')

    def FindChatID(self,userID):
        chat_dict1=requests.get(f'{self.URL}/catalog/{userID}/chatID') # ottengo  dal catalog la chatID dell'utente associato alla stanza
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
        print(f"Message received! Everything works correctly! Topic: {topic}, Measure: {payload['e'][0]['n']}, Value: {payload['e'][0]['v']},  Measure: {payload['e'][1]['n']}, Value: {payload['e'][1]['v']}, Timestamp: {payload['e'][0]['t']} with QoS: {qos}")
        
        temval = payload['e'][0]['v']
        humval = payload['e'][1]['v']
        r_TS = requests.get(f'{self.URL}/catalog/{self.roomID}/TS_utilities') # ottengo le utilities di Thing Speak dal catalog 
     
        if r_TS.status_code==200 and len(self.field_field["field"])==2:
            j_TS = json.dumps(r_TS.json(),indent=4)
            d_TS = json.loads(j_TS)
            TS=d_TS["ThingSpeak"]
            message1=self.__message1
            message1["TS_api"]=TS["api_key_write"]
            message1["ThingSpeak_field"]=self.field_field["field"][0]
            message1["v"]=temval 
            time.sleep(3) 
            topic_TS = requests.get(f'{self.URL}/catalog/Thingspeak_API')   # richiesta al catalog delle API del canale ThingSpea
            if topic_TS.status_code==200:
                topic_TS1 = json.dumps(topic_TS.json(),indent=4)
                topic_TS = json.loads(topic_TS1)
                TS_topic=topic_TS["Thingspeak_API"]["mqttTopicThingspeak"]
                if TS_topic!='':
                    self.device.myPublish(TS_topic,message1) 
            #self.device.myPublish("ThingSpeak/channel/allsensor",message1)
            message2=self.__message1
            message2["TS_api"]=TS["api_key_write"]
            message2["ThingSpeak_field"]=self.field_field["field"][1]
            message2["v"]=humval
            time.sleep(3)
            if TS_topic!='':
                self.device.myPublish(TS_topic,message2)
        ranges_dict1=requests.get(f'{self.URL}/catalog/{self.roomID}/ranges') #richista dei range di corretto funzionamento del device 
        if ranges_dict1.status_code==200:
            ranges_dict2= json.dumps(ranges_dict1.json(),indent=4)
            ranges_dict = json.loads(ranges_dict2)
            alert_val_temp=ranges_dict["ranges"]["Temperature"]
            alert_val_hum=ranges_dict["ranges"]["Humidity"]
        else:
            raise Exception(f"Request status code: {ranges_dict1.status_code},Error occurred!")
        msg_bot=self.__msg_bot1
        users_dict1=requests.get(f'{self.URL}/catalog/{self.roomID}/users') #richiesta degli user associati alla stanza
        if users_dict1.status_code==200:
            # print(users_dict1)
            users_dict2= json.dumps(users_dict1.json(),indent=4)
            users_dict = json.loads(users_dict2)
################## TEMPERATURE ####################################
            if ((float(temval)>= float(alert_val_temp[1])) or (float(temval) <= float(alert_val_temp[0]))): #controllo se il messaggio pubblicato è nel range di normalità sia per tem 
              
                for user in users_dict["user"]:
                    if 'M_' not in user: # il messaggio viene inviato agli utenti associati alla stanza non ai manager
                        chatID=self.FindChatID(user)
                        if chatID!=None:
                            msg_bot["measure_type"]='temperature'
                            msg_bot["ranges"] = alert_val_temp
                            msg_bot["value"] = temval
                            msg_bot["Room"] = self.roomID
                            msg_bot["chatID"] = chatID
                            self.device.myPublish(f"BOT/{self.Generaltopic}/alarm/{self.roomID}/{self.deviceID}",msg_bot) # pubblicazione del messaggio di allarme al bot telegram
############## HUMIDITY #############################################
            if ((float(humval)>= float(alert_val_hum[1])) or (float(humval) <= float(alert_val_hum[0]))):#controllo se il messaggio pubblicato è nel range di normalità  
                
                msg_bot=self.__msg_bot1
                # print(f'{self.URL}/catalog/{self.roomID}/users')
                # users_dict1=requests.get(f'{self.URL}/catalog/{self.roomID}/users')
                # print(users_dict1)
                # users_dict2= json.dumps(users_dict1.json(),indent=4)
                # users_dict = json.loads(users_dict2)
                # print(users_dict)
                if len(users_dict)>0:
                    for user in users_dict['user']:
                        if 'M_' not in user:
                            chatID=self.FindChatID(user)
                            if chatID!=None:
                                msg_bot["measure_type"]='humidity'
                                msg_bot["ranges"] = alert_val_hum
                                msg_bot["value"] = humval
                                msg_bot["Room"] = self.roomID
                                msg_bot["chatID"] = chatID
                                time.sleep(6)
                                self.device.myPublish(f"BOT/{self.Generaltopic}/alarm/{self.roomID}/{self.deviceID}",msg_bot)# pubblicazione del messaggio di allarme al bot telegram
                        
        
    def getRoom(self):
        return json.dumps({"roomID": self.roomID})
    
    def getDeviceID(self):
        return json.dumps({"deviceID": self.deviceID})



if __name__ == "__main__":

    myDevicesList = []
    current_rooms = []

    f = open('Settings.json')
    data = json.load(f)
    URL = data["catalogURL"] ### apertura dai setting del file contenente indirizzo del catalog
    #print(URL)
    # Get all the rooms currently used
    r_rooms = requests.get(f'{URL}/catalog/rooms') # richiesta al catalog delle stanze disponibili 
    # print(r_rooms)
    
    if r_rooms.status_code == 200:
        j_rooms = json.dumps(r_rooms.json(),indent=4)
        d_rooms = json.loads(j_rooms)
        current_rooms_list = d_rooms["roomList"] #Note: rooms is a list
        for room in current_rooms_list:
            current_rooms.append(room["roomID"])
    
        # For all the rooms take all the smoke devices
        for room in current_rooms:
            r_devices = requests.get(f'{URL}/catalog/{room}/measure_type/temphum') # richiesta dei device che misurano temperatura/umidità nelle stanze
            if r_devices.status_code == 200:
                j_devices = json.dumps(r_devices.json(),indent=4)
                d_devices = json.loads(j_devices)
                devices = d_devices["foundIDs"] #Note: devices is a list
                # print(devices)
                # Create a thread for each device
                for device in devices:
                    myDevicesList.append(TEMPHUMReceiver(device,room,URL)) # inserimento in una lista di subscriber dei dati pubblicati dai device 
                    print(f"New device added: {device}")

        for device in myDevicesList:
            device.start() # avvio del thread

    # Keep updating the previous devices
    while True:
        time.sleep(30)
        # Get all the updated rooms
        update_rooms = []
        
        r_rooms = requests.get(f'{URL}/catalog/rooms') # richiesta delle stanze
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
                        device.stop() # se il device è nella lista delle stanze da rimuovere fermo il tread e inserisco il device 
                        device_to_delete.append(json.loads(device.getDeviceID())["deviceID"]) 
            for del_device in device_to_delete:
                for i, device in enumerate(myDevicesList):
                    if del_device == json.loads(device.getDeviceID())["deviceID"]:
                        del myDevicesList[i]

            # Check for changes in the remaining rooms
            for room in current_rooms:
                r_devices = requests.get(f'{URL}/catalog/{room}/measure_type/temphum')
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
                        myDevicesList.append(TEMHUMReceiver(device,room,URL)) # parte il thread per i debive che non sono precenti nella lista iniziale 
                        myDevicesList[-1].start()
                        print(f"New device added: {device}")

            # Find all the devices to add from new rooms
            # Rooms that must be added
            rooms_to_add = list(set(update_rooms) - set(current_rooms)) 
            # Add that rooms to current rooms
            current_rooms = current_rooms + rooms_to_add
            # Add all the devices within the rooms to add
            for room in rooms_to_add:
                r_devices = requests.get(f'{URL}/catalog/{room}/measure_type/temphum')
                if r_devices.status_code == 200:
                    j_devices = json.dumps(r_devices.json(),indent=4)
                    d_devices = json.loads(j_devices)
                    devices = d_devices["foundIDs"] #Note: devices is a list
                    # Create a thread for each device
                    for device in devices:
                        myDevicesList.append(TEMHUMReceiver(device,room,URL))# si aggiunge alla lista e si fa partire l'ultimo aggiunto di volta in volta
                        myDevicesList[-1].start()
                        print(f"New device added: {device}")