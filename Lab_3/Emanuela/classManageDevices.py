import json
from datetime import datetime

class ListDevice():
    def __init__(self):
       
       self.LastUpdate=()
       self.catalog=json.load(open('catalog.json','r'))
       self.catalog_dev={"projectOwner":"Jake Blues",
                         "projectName":"MySmartThingy",
                         "lastUpdate":[],
                         "devicesList":[]}
    def searchByName(self,deviceName):
        devlist=[]
        for device in self.catalog['devicesList']:
            if device['deviceName']==deviceName:
                devlist.append(device)
        d=json.dumps(devlist,indent=4)
        return d   
    def searchbyID(self,ID):
        devlist=[]
        for device in self.catalog['devicesList']:
            if device['deviceID']==ID:
                devlist.append(device)
        d=json.dumps(devlist,indent=4)
        return d
        
    def searchbyservice(self,service):
        devlist=[]
        for device in self.catalog['devicesList']:
            listaservices=device["availableServices"]
            if service in listaservices:
                devlist.append(device)
        d=json.dumps(devlist,indent=4)
        return d
        
    def searchbyMeasureType(self,measuretype):
        devlist=[]
        for device in self.catalog['devicesList']:
            measuretypelist=device["measureType"]
            if measuretype in measuretypelist:
                devlist.append(device)
        d=json.dumps(devlist,indent=4)
        return d

    def insert_device(self,insertdevice):
        ID_catalog=[]
        dev=insertdevice['device']
        ID=((dev['deviceID']))
        modifica=insertdevice['modifica']
        new_device=dev
        DeviceList=[]
        for device in self.catalog['devicesList']:
            ID_catalog.append(device["deviceID"])
        if ID in (ID_catalog):
            print(ID,ID_catalog)
            if modifica=='y':
                Now=datetime.now()
                dt_string = Now.strftime("%Y-%m-%d %H:%M")
                self.catalog_dev["lastUpdate"]=dt_string
                for device in self.catalog['devicesList']:
                    if ID==device["deviceID"]:
                        DeviceList.append(new_device) 
                               
                    else:
                        DeviceList.append(device)
                    
                self.catalog_dev['devicesList']=DeviceList
                print(json.dumps(self.catalog_dev))
                return(json.dumps(self.catalog_dev))


            else:
                self.catalog_dev['devicesList']=self.catalog['devicesList']
                print(json.dumps(self.catalog_dev))
                return(json.dumps(self.catalog_dev))
                
        else:
            Now=datetime.now()
            dt_string = Now.strftime("%Y-%m-%d %H:%M")
            self.catalog_dev["lastUpdate"]=dt_string
            self.catalog['devicesList'].append(new_device)
            self.catalog_dev['devicesList']=self.catalog['devicesList']
            print(self.catalog_dev)
            return(json.dumps(self.catalog_dev))
           
        
    def exit(self):
        self.LastUpdate=self.catalog["lastUpdate"]
        if self.LastUpdate != self.catalog_dev["lastUpdate"] and self.catalog_dev["lastUpdate"]!=[]:
            json.dump(self.catalog_dev,open('catalog.json','w'))
            d=json.dumps(self.catalog_dev,indent=4)
        else: 
           json.dump(self.catalog,open('catalog.json','w'))
           d=json.dumps(self.catalog,indent=4)
        return d 
        
    def printall(self):
        d=json.dumps(self.catalog,indent=4)
        return d