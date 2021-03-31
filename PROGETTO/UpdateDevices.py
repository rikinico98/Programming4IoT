# Receive MQTT messages from all devices and check if some of them is not working anymore
# If so, send a DELETE request to Warehouse_Catalog.py
# Note: if the device was already deleted from the catalog this step is useless, but it is done the same.



from MyMQTT import *
import time
import json
import requests



class UpdateDevices():

    def __init__(self, ID):
        self.ID = ID
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
        self.up_dev = MyMQTT(self.ID, self.broker, self.port, self)
        # Request topic from catalog
        self.topic = "WareHouse/team5/#"
        # Define the last received timestamp
        self.lastReceivedTime = {
            "devices": []
        }

    def start(self):
        self.up_dev.start()
        self.up_dev.mySubscribe(self.topic)

    def stop(self):
        self.up_dev.stop()

    def notify(self, topic, msg, qos):
        payload = json.loads(msg)
        device_ID = payload['bn']
        timestamp = payload['e'][0]['t']
        print(f"Message received! Device: {device_ID}, Timestamp: {timestamp}")
        # Get device ID and room ID
        devices = self.lastReceivedTime["devices"]
        room = topic.split('/')[2]
        # If there is no devices in memory, add it
        if devices == []:
            myDict = {
                "deviceID": device_ID,
                "roomID": room,
                "timestamp": timestamp
            }
            devices.append(myDict)
        else:
            # Else check if device is already present
            flag_ID = 1
            for device in devices:
                if device["deviceID"] == device_ID:
                    flag_ID = 0
                    # If so, update its timestamp
                    device["timestamp"] = timestamp
                    # Send a request to update it in the catalog
                    requests.put(f'http://127.0.0.1:8070/catalog/{device["roomID"]}/{device["deviceID"]}/update_timestamp', data = json.dumps({"timestamp": timestamp}))
            if flag_ID == 1:
                # Else insert a new device in memory
                myDict = {
                    "deviceID": device_ID,
                    "roomID": room,
                    "timestamp": timestamp
                }
                devices.append(myDict)
    
    def returnDevices(self):
        return json.dumps({"devices": self.lastReceivedTime})

    def deleteDevice(self, device):
        self.lastReceivedTime["devices"].remove(device)



if __name__ == "__main__":
    up_device = UpdateDevices("UpdateDevices_Wharehouse_Team5")
    up_device.start()
    while True:
        # Check if some of the devices is expired
        # expired: it do not publish any message for more than 2 minutes
        now = time.time()
        devices = json.loads(up_device.returnDevices())["devices"]
        flag = 1
        for device in devices["devices"]:
            time_diff = now - float(device["timestamp"])
            if time_diff > 120:
                # Delete the device because it is expired!!!
                flag = 0
                requests.delete(f'http://127.0.0.1:8070/catalog/{device["roomID"]}/{device["deviceID"]}/delete')
                to_remove = device
        if flag == 0:
            up_device.deleteDevice(to_remove)
        time.sleep(5)
    up_device.stop()