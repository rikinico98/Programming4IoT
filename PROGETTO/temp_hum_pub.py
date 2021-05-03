#TEMP HUM sensor simulator
# PUBLISHER DI TEMPERATURA E UMIDITA'

from MyMQTT import *
import threading
import json
import time
import random
import requests
import math
import numpy as np

class MyThread(threading.Thread):

    def __init__(self,roomID, threadID, device, failure,URL,roomtype):
        self.URL=URL
        self.roomtype=roomtype
        ranges_dict1=requests.get(f'{self.URL}/catalog/{roomID}/ranges') ######## richiesta al catalog dei range delle stanze
        if ranges_dict1.status_code==200:
            ranges_dict2= json.dumps(ranges_dict1.json(),indent=4)
            ranges_dict = json.loads(ranges_dict2)
            self.alert_val_temp=ranges_dict["ranges"]["Temperature"]
            self.alert_val_hum=ranges_dict["ranges"]["Humidity"]
            self.loc1=np.mean(self.alert_val_temp) # la pubblicazione avverrà sulla media del range di corretto funzionamento
            self.loc2=np.mean(self.alert_val_hum)
            
            if self.roomtype=='10' or self.roomtype=='01': # differenzio i range di fallimento a seconda del tipo di stanza in questione, se la stanza è freezer non necessita del range inferiore 
                self.failuretemprange=list(np.arange(0,self.alert_val_temp[0]-1,0.01))+list(np.arange(self.alert_val_temp[1]-1,50,0.01))+list(np.arange(self.alert_val_temp[0],self.alert_val_temp[1],0.01))
                self.failurehumrange=list(np.arange(0,self.alert_val_hum[0]-1,0.01))+list(np.arange(self.alert_val_hum[1]-1,90,0.01))+list(np.arange(self.alert_val_hum[1],self.alert_val_hum[1],0.01))
            else:
                self.failuretemprange=list(np.arange(self.alert_val_temp[1]+1,50,0.01))+list(np.arange(self.alert_val_temp[0],self.alert_val_temp[1],0.01)) 
                self.failurehumrange=list(np.arange(self.alert_val_hum[1]+1,90,0.01))+list(np.arange(self.alert_val_hum[1],self.alert_val_hum[1],0.01)) 
            #massima temp=50°C massima umidità =90%. Valori inseriti considerando un tipico esempio di sensore di temperatura
                
            threading.Thread.__init__(self)
            #Setup thread
            self.threadID = threadID
            self.device = device
            self.iterate = True
            self.failure = failure
            
        else:
            raise Exception(f"Request status code: {ranges_dict1.status_code},Error occurred!")
        

    def run(self):
        while self.iterate:
            p = random.uniform(0,1)
            time.sleep(900)
            if p > self.failure: # se il valore p estratto è maggiore del valore di fallimento allora si è  in una condizione di normalità
                loc, scale = self.loc1, 0.1
                a= np.random.logistic(loc, scale, 10000) # simulazione dei dati temperatura, questa distribuzione consente di avere dei dati attorno allo stesso valore ben simulando una condizione controllata
                u = random.choice(a)
                loc, scale = self.loc2, 0.1
                b= np.random.logistic(loc, scale, 10000) # simulazione per l'umidità
                v = random.choice(b)
                

               
            else:
                print("fallimento") # simuazione del fallimento prendendo random uno dei numeri presenti nelle liste di fallimento 
                a=random.randint(0,len(self.failuretemprange)-1)
                u = self.failuretemprange[a]
                b=random.randint(0,len(self.failurehumrange)-1)
                v= self.failurehumrange[b]
                print(u,v)

            if (u >=self.alert_val_temp[0] and u<= self.alert_val_temp[1] ) and (v>= self.alert_val_hum[0] and v<= self.alert_val_hum[1]):
                # Everything works!
                print('Everything works!')
                
                self.device.publish(u,v)
             
            
            else:
                # Simulation of failure (failure holds for some time until resolution of the problem)
                # Keep sending the wrong result to simulate the time needed to solve the problem
                time_to_solve = math.ceil(random.uniform(5,15)) 
                print(f'tempo in cui si ripete il problema: {time_to_solve}')
                for it in range(time_to_solve):
                    self.device.publish(u,v)
                    time.sleep(900)
                
    
    def stop(self):
        self.iterate = False


class TEMHUMSensor():

    def __init__(self, ID, deviceID, roomID, failure,URL):
        self.URL=URL
        self.ID = ID
        self.deviceID = deviceID
        self.roomID = roomID
        self.failure = failure
        # Request broker from catalog
        r_broker = requests.get(f'{self.URL}/catalog/MQTT_utilities') #richiesta al catalog del broker, della porta e del topic generale
        if r_broker.status_code==200:
            j_broker = json.dumps(r_broker.json(),indent=4)
            d_broker = json.loads(j_broker)
            self.broker = d_broker["MQTT_utilities"]["msgBroker"]
            self.port = d_broker["MQTT_utilities"]["port"]
            # Create the device
            self.device = MyMQTT(self.ID, self.broker, self.port, None)
        # Request topic from catalog
        r_topic = requests.get(f'{self.URL}/catalog/{self.roomID}/{self.deviceID}/topic') # richiesta al catalog del topic specifico del dispositivo 
        if r_topic.status_code==200:
            j_topic = json.dumps(r_topic.json(),indent=4)
            d_topic = json.loads(j_topic)
            self.topic = d_topic["topic"] #Note: topic is a list
            # Define standard message to send
        else:
            raise Exception(f"Request status code: {r_topic.status_code},Error occurred!")
        self.__message = {"bn": self.deviceID, "e": [{"n": "temp detector", "u": "C", "t": None, "v": None},{"n": "hum detector", "u": "g/m^3", "t": None, "v": None}]}
        
        r_roomtype = requests.get(f'{self.URL}/catalog/{self.roomID}/assigned_product_type') #richiesta al catalog del tipo di stanza 
        if r_roomtype.status_code==200:
            j_roomtype = json.dumps(r_roomtype.json(),indent=4)
            d_roomtype = json.loads(j_roomtype)
            self.roomtype = (d_roomtype["product_type"]) #Note: topic is a list
            
        else:
            raise Exception(f"Request status code: {r_roomtype.status_code},Error occurred!")
        print(f'Room ID: {self.roomID}, Device ID:{self.deviceID}, Product type:{self.roomtype}')
        
    def start(self):
        self.device.start()
        self.device_thread = MyThread(self.roomID,self.ID, self, self.failure,self.URL,self.roomtype)
        self.device_thread.start()

    def stop(self):
        self.device_thread.stop()
        self.device.stop()

    def publish(self, valueT, valueH):
        message=self.__message
        # Add timestamp
        valueH="{:.2f}".format(valueH)
        valueT="{:.2f}".format(valueT)
        message["e"][0]["t"] = str(time.time()) 
        # Add value

        message["e"][0]["v"] = valueT
        # Add value
        message["e"][1]["v"] = valueH
        message["e"][1]["t"] =str(time.time())
        # Publish to all the topics
        for topic in self.topic:
            print(topic)
            self.device.myPublish(topic, message)

    def getRoom(self):
        return json.dumps({"roomID": self.roomID})
    
    def getDeviceID(self):
        return json.dumps({"deviceID": self.deviceID})


if __name__ == "__main__":
    f = open('Settings.json')
    data = json.load(f)
    URL = data["catalogURL"] # ottenimento dell'indirizzo del catalog dal file di settings
    # To simulate failure of the real sensor
    failure_probability = -1
    while failure_probability < 0 or failure_probability > 1: #inserimento di una probabilità di errore per simulare situazioni critiche 
        failure_probability = float(input("Insert the failure probability to simulate\nNote: it must be a number in [0,1]\n"))

    myDevicesList = []
    current_rooms = []
    # Get all the rooms currently used
    r_rooms = requests.get(f'{URL}/catalog/rooms') #richiesta delle stanze al catalog 
    if r_rooms.status_code == 200:
        j_rooms = json.dumps(r_rooms.json(),indent=4)
        d_rooms = json.loads(j_rooms)
        current_rooms_list = d_rooms["roomList"] #Note: rooms is a list
        for room in current_rooms_list:
            current_rooms.append(room["roomID"])
            
    
        # For all the rooms take all the smoke devices
        for room in current_rooms:
            r_devices = requests.get(f'{URL}/catalog/{room}/measure_type/temphum') #richiesta dei device che pubblicano temperatura e umidità per la stanza 
            if r_devices.status_code == 200:
                j_devices = json.dumps(r_devices.json(),indent=4)
                d_devices = json.loads(j_devices)
                devices = d_devices["foundIDs"] #Note: devices is a list
                # Create a thread for each device
                for device in devices:
                    myDevicesList.append(TEMHUMSensor(device+"_pub", device, room, failure_probability,URL))
                    print(f"New device added: {device}")

        for device in myDevicesList:
            time.sleep(20)
            device.start()

    # Keep updating the previous devices
    while True:
        time.sleep(30)
        # Get all the updated rooms
        update_rooms = []
        r_rooms = requests.get(f'{URL}/catalog/rooms') # nuova richiesta delle stanze 
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
                        device.stop() # stop del thread del device da eliminare 
                        device_to_delete.append(json.loads(device.getDeviceID())["deviceID"])
            for del_device in device_to_delete:
                for i, device in enumerate(myDevicesList):
                    if del_device == json.loads(device.getDeviceID())["deviceID"]:
                        del myDevicesList[i]

            # Check for changes in the remaining rooms
            for room in current_rooms:
                r_devices = requests.get(f'{URL}/catalog/{room}/measure_type/temphum') #richiesta dei device di temperatura e umidità per la stanza 
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
                        myDevicesList.append(TEMHUMSensor(device+"_pub", device, room, failure_probability,URL))
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
                        myDevicesList.append(TEMHUMSensor(device+"_pub", device, room, failure_probability,URL))
                        myDevicesList[-1].start()
                        print(f"New device added: {device}")