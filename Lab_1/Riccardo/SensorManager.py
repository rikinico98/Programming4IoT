import json
from datetime import datetime

class ServiceDetails():
    def __init__(self,serviceType,serviceIP,topic):
        self.serviceType=serviceType
        self.serviceIP=serviceIP
        self.topic=[]
        if topic != 0:
            for tp in topic:
                self.topic.append(tp)

    def __repr__(self):
        return "{},{},{}".format(self.serviceType, self.serviceIP, self.topic)


class Sensor(ServiceDetails):

        def __init__(self, deviceID,deviceName, measureType, availableServices,lastUpdate, servicesDetails):
            self.deviceID = deviceID
            self.deviceName = deviceName
            self.measureType = measureType
            self.availableServices= availableServices
            self.lastUpdate=lastUpdate
            self.servicesDetails=[]
            for service in servicesDetails:
                if 'topic' in service.keys():
                    self.servicesDetails.append(ServiceDetails(service['serviceType'],service['serviceIP'],\
                                                    service['topic']))
                else:
                    self.servicesDetails.append(ServiceDetails(service['serviceType'], service['serviceIP'],0))


        def __repr__(self):
            return "{},{},{},{},{}".format(\
                                              self.deviceID, self.deviceName,\
                                              self.measureType,self.availableServices,\
                                              self.servicesDetails)

class SensorManager():
        def __init__(self,fileName):
            self.devicesList= []
            self.jsonContent={}
            self.fileName = fileName
            td = json.load(open(self.fileName))
            self.projectOwner=td["projectOwner"]
            self.projectName=td["projectName"]
            self.lastUpdate=td["lastUpdate"]
            for device in td["devicesList"]:
                self.devicesList.append(Sensor(device['deviceID'],device['deviceName'],\
                                            device['measureType'],device['availableServices'],\
                                            device['lastUpdate'],device['servicesDetails']))
        def __repr__(self):
            return '{},{},{},{}'.format(\
                                              self.projectOwner, self.projectName,\
                                               self.lastUpdate,self.devicesList)


        def searchByName(self,deviceName):
            found=1
            for device in self.devicesList:
                if device.deviceName == deviceName:
                    print(device)
                    found=0
            if found:
                print('Device non trovato!!!!')


        def searchByID(self,deviceID):
            for device in self.devicesList:
                if device.deviceID == deviceID:
                    print(device)
                    return
            print('Device non trovato!!!!')
        def searchByMeasureType(self,measureType):
            found=1
            for device in self.devicesList:
                for type in device.measureType:
                    if (type == measureType):
                        print(device)
                        found = 0
            if found:
                print('Device non trovato!!!!')


        def insertDevice(self,to_add):
            found=0
            for device in self.devicesList:
                if device.deviceID == to_add['deviceID']:
                    found=1
                    print("ATTENZIONE DEVICE GIA' PRESENTE!!!\nAGGIORNARE I DATI?")
                    choice=input('Digitare Y/N\n')
                    if choice =='Y':
                        device.deviceName = to_add['deviceName']
                        device.measureType =  to_add['measureType']
                        device.availableServices = to_add['availableServices']
                        device.lastUpdate = to_add['lastUpdate']
                        device.servicesDetails = []
                        for service in to_add['servicesDetails']:
                            if 'topic' in service.keys():
                                device.servicesDetails.append(ServiceDetails(service['serviceType'], service['serviceIP'], \
                                                                           service['topic']))
                            else:
                                device.servicesDetails.append(
                                    ServiceDetails(service['serviceType'], service['serviceIP'], 0))
            if not found:
                device.deviceName = to_add['deviceName']
                device.deviceID = to_add['deviceID']
                device.measureType = to_add['measureType']
                device.availableServices = to_add['availableServices']
                device.lastUpdate = to_add['lastUpdate']
                device.servicesDetails = []
                for service in to_add['servicesDetails']:
                    if 'topic' in service.keys():
                        device.servicesDetails.append(ServiceDetails(service['serviceType'], service['serviceIP'], \
                                                                     service['topic']))
                    else:
                        device.servicesDetails.append(
                            ServiceDetails(service['serviceType'], service['serviceIP'], 0))






        def printAll(self):
            Catalog={}
            Catalog["projectOwner"]=self.projectOwner
            Catalog["projectName"]=self.projectName
            Catalog["lastUpdate"]=self.lastUpdate
            Catalog['devicesList']=[]
            for device in self.devicesList :
                details=[]
                for detail in device.servicesDetails:
                    det=dict(serviceType=detail.serviceType,serviceIP=detail.serviceIP,\
                             topic=detail.topic)
                    details.append(det)
                dev=dict( deviceName= device.deviceName, deviceID= device.deviceID,\
                           measureType =device.measureType,availableServices=device.availableServices,\
                           lastUpdate=device.lastUpdate,servicesDetails=details)
                Catalog['devicesList'].append(dev)

            self.jsonContent=Catalog
            print(Catalog)


        def save_all(self):
            json.dump(self.jsonContent, open(self.fileName, 'w', ), indent=4)


