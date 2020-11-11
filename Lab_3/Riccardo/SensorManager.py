import json
from datetime import datetime

class SensorManager():
        def __init__(self,fileName,catalog):

            self.jsonContent={}
            self.fileName = fileName
            self.td = json.loads(catalog)


        def searchByName(self,deviceName):
            found=1
            found_devices=[]
            for device in self.td['devicesList']:
                if device['deviceName'] == deviceName:
                    found_devices.append(device)
                    found=0
            if found:
                print('Device non trovato!!!!')
            return found_devices


        def searchByID(self,deviceID):
            for device in self.td['devicesList']:
                if device['deviceID'] == int(deviceID):
                    return device
            print('Device non trovato!!!!')

        def searchByMeasureType(self,measureType):
            found=1
            found_devices = []
            for device in self.td['devicesList']:
                for type in device['measureType']:
                    if (type == measureType):
                        found_devices.append(device)
                        found = 0
            if found:
                print('Device non trovato!!!!')
            return found_devices


        def insertDevice(self,to_add):
            found=0
            for device in self.td['devicesList']:
                if device['deviceID']== to_add['deviceID']:
                    found=1
                    device['deviceName '] = to_add['deviceName']
                    device['measureType '] = to_add['measureType']
                    device['availableServices'] = to_add['availableServices']
                    device['lastUpdate'] = datetime.today().strftime('%Y-%m-%d-%H:%M')
                    self.td['lastUpdate'] = datetime.today().strftime('%Y-%m-%d-%H:%M')
                    device['servicesDetails'] = []
                    for service in to_add['servicesDetails']:
                        if 'topic' in service.keys():
                            device['servicesDetails'].append(
                                dict(serviceType=service['serviceType'], service=['serviceIP'], \
                                     topic=service['topic']))
                        else:
                            device['servicesDetails'].append(
                                dict(serviceType=service['serviceType'], service=['serviceIP']))

            if not found:
                device_new={}
                device_new['deviceName '] = to_add['deviceName']
                device_new['deviceID']=to_add['deviceID']
                device_new['measureType '] = to_add['measureType']
                device_new['availableServices'] = to_add['availableServices']
                device_new['lastUpdate'] = datetime.today().strftime('%Y-%m-%d-%H:%M')
                self.td['lastUpdate'] = datetime.today().strftime('%Y-%m-%d-%H:%M')
                device_new['servicesDetails'] = []
                for service in to_add['servicesDetails']:
                    if 'topic' in service.keys():
                        device_new['servicesDetails'].append(dict(serviceType=service['serviceType'], service=['serviceIP'], \
                                                              topic=service['topic']))
                    else:
                        device_new['servicesDetails'].append(
                            dict(serviceType=service['serviceType'], service=['serviceIP']))
                self.td['devicesList'].append(device_new)







        def printAll(self):

            for key, value in self.td.items():
                if key == 'devicesList':
                    devices=self.td['devicesList']
                    print('devicesList : \n')
                    i=1
                    for device in devices:
                        print('DEVICE',i,':\n')
                        i=i+1
                        for key_s, value_s in device.items():
                            print(key_s, ' : ', value_s)


                else:
                    print(key, ' : ', value)


        def save_all(self):
            json.dump(self.td, open(self.fileName, 'w', ), indent=4)


