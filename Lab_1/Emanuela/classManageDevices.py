from datetime import datetime
import json

class ManageDevices():

    def __init__(self, fileName):
        self.fileName = fileName
        jsonFile = open(self.fileName,"r")
        self.dict = json.load(jsonFile)
        jsonFile.close()
        self.devicesList = self.dict["devicesList"]

    def searchByName(self, name):
        solutions = []
        for it in range(len(self.devicesList)):
            if self.devicesList[it]["deviceName"] == name:
                solutions.append(self.devicesList[it])
        return solutions

    def searchByID(self,ID):
        solutions = []
        for it in range(len(self.devicesList)):
            if self.devicesList[it]["deviceID"] == ID:
                solutions.append(self.devicesList[it])
        return solutions

    def searchByService(self,service):
        solutions = []
        for it in range(len(self.devicesList)):
            serviceList = self.devicesList[it]["servicesDetails"]
            for it2 in range(len(serviceList)):
                if serviceList[it2]["serviceType"] == service:
                    solutions.append(self.devicesList[it])
        return solutions

    def searchByMeasureType(self,Mtype):
        solutions = []
        for it in range(len(self.devicesList)):
            measureType = self.devicesList[it]["measureType"]
            for it2 in range(len(measureType)):
                if measureType[it2] == Mtype:
                    solutions.append(self.devicesList[it])
        return solutions

    def insertDevice(self, ID):
        update = None
        numFeature = None
        numFeature2 = None
        value = None
        now = datetime.now()
        for it in range(len(self.devicesList)):
            if self.devicesList[it]["deviceID"] == ID:
                update = int(input("Device already exists, update it?\n [1] YES\n [2] NO\n"))
                if update == 1:
                    self.devicesList[it]["deviceName"] = input("Insert the new name ")
                    self.devicesList[it]["measureType"][:] = []
                    numFeature = int(input("How much measure need to be insert? "))
                    for it2 in range(numFeature):
                        value = input()
                        self.devicesList[it]["measureType"].append(value)
                    self.devicesList[it]["availableServices"][:] = []
                    self.devicesList[it]["servicesDetails"][:]=[]
                    serviceDict = []
                    numFeature = int(input("How much services need to be insert? "))
                    for it2 in range(numFeature):
                        topicList = []
                        value = input()
                        self.devicesList[it]["availableServices"].append(value)
                        serviceDict = {}
                        serviceType = input("Insert the service type ")
                        serviceDict[it2].update({'serviceType' : serviceType})
                        serviceIP = input("Insert the service IP ")
                        serviceDict[it2].update({'serviceIP' : serviceIP})
                        numFeature2 = int(input("How many topic to insert? "))
                        for it3 in range (numFeature2):
                            value = input()
                            topicList.append(value)
                        serviceDict[it2].update({'topic' : topicList})
                        self.devicesList[it]["servicesDetails"].append(serviceDict)
                    self.devicesList[it]["lastUpdate"] = now.strftime("%Y-%m-%d %H:%M")
                    return
                elif update == 2:
                    return None
                else:
                    print("Non valid answer")
                    return None
        listType = []
        listServices = []
        topicList = []
        numFeature = int(input("How much measure need to be insert? "))
        for it in range(numFeature):
            value = input()
            listType.append(value)
        numFeature2 = int(input("How much services need to be insert? "))
        serviceDict = []
        for it in range(numFeature2):
            serviceDict.append({})
            value = input()
            listServices.append(value)
            serviceType = input("Insert the service type ")
            serviceDict[it].update({'serviceType' : serviceType})
            serviceIP = input("Insert the service IP ")
            serviceDict[it].update({'serviceIP' : serviceIP})
            numFeature = int(input("How many topic to insert? "))
            for it2 in range (numFeature):
                value = input()
                topicList.append(value)
                serviceDict[it].update({'topic' : topicList})
        newDictionary = {
            "deviceID" : ID,
            "deviceName" : input("Insert name "),
            "measureType" : listType,
            "availableServices" : listServices,
            "servicesDetails" : serviceDict,
            "lastUpdate" : now.strftime("%Y-%m-%d %H:%M")
        }
        self.devicesList.append(newDictionary)
        return       

    def printAll(self):
        return self.devicesList

    def exit(self):
        now = datetime.now()
        newDict = {
            "projectOwner" : self.dict["projectOwner"],
            "projectName" : self.dict["projectName"],
            "lastUpdate" : now.strftime("%Y-%m-%d %H:%M"),
            "devicesList" : self.devicesList
        }
        jsonFile = open(self.fileName,"w")
        jsonFile.write(json.dumps(newDict,indent=4))
        jsonFile.close()