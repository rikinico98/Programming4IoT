from datetime import datetime


class DeviceManager:
    def __init__(self):
        pass

    def findTopic(self, catalog, roomID, deviceID):
        ###############################
        # Returned flags#
        # 2 ---> if room is found device IS NOT FOUND
        # 3 ---> room IS NOT FOUND
        # 0 ---> if room is found device is found
        ###############################
        topic = []
        for room in catalog['roomList']:
            if room['roomID'] == roomID:
                device, deviceFound = self.__searchByID(room, deviceID)
                if deviceFound == 1:
                    # intero che viene usato nella classe a livello
                    # superiore per identificare l'errore
                    flag = 2
                    return topic, flag
                else:
                    for service in device['servicesDetails']:
                        if service["serviceType"] == "MQTT":
                            topic = service['topic']
                    flag = 0
                    return topic, flag
        flag = 3
        return topic, flag

    def addNewDevice(self, catalog, newDevice, roomID, deviceID):
        ###############################
        # Returned flags#
        # 2 ---> if room is found device IS NOT FOUND
        # 3 ---> room IS NOT FOUND
        # 0 ---> if room is found device is found
        ###############################
        roomFound = 1
        deviceFound = 1
        room = None
        for room in catalog['roomList']:
            if room['roomID'] == roomID:
                roomFound = 0
                device, deviceFound = self.__searchByID(room, deviceID)
        if deviceFound == 1 and roomFound == 1:
            flag = 3
            return catalog, flag
        elif deviceFound == 0 and roomFound == 0:
            flag = 0
            return catalog, flag
        elif deviceFound == 1 and roomFound == 0:
            flag = 2
            device_new = {
                'deviceName': newDevice['deviceName'],
                'deviceID': newDevice['deviceID'],
                'measureType': newDevice['measureType'],
                'availableServices': newDevice['availableServices'],
                'servicesDetails': [],
                'ThingSpeak':[]}
            for service in newDevice['servicesDetails']:
                if 'topic' in service.keys():
                    device_new['servicesDetails'].append(
                        dict(
                            serviceType=service['serviceType'],
                            serviceIP=service['serviceIP'],
                            topic=service['topic']))
                else:
                    device_new['servicesDetails'].append(
                        dict(
                            serviceType=service['serviceType'],
                            serviceIP=service['serviceIP'],
                            topic=[]))
            dateTimeObj = datetime.now()
            currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second}"
            device_new['lastUpdate'] = currentTime
            catalog['lastUpdate'] = currentTime
            room['lastUpdate'] = currentTime
            room['devicesList'].append(device_new)
            return catalog, flag

    def deleteDevice(self, catalog, roomID, deviceID):
        ###############################
        # Returned flags#
        # 2 ---> if room is found device IS NOT FOUND
        # 3 ---> room IS NOT FOUND
        # 0 ---> if room is found device is found
        ###############################
        roomFound = 1
        deviceFound = 1
        device = None
        room = None
        for room in catalog['roomList']:
            if room['roomID'] == roomID:
                roomFound = 0
                device, deviceFound = self.__searchByID(room, deviceID)
        if deviceFound == 1 and roomFound == 1:
            flag = 3
            return catalog, flag
        elif deviceFound == 1 and roomFound == 0:
            flag = 2
            return catalog, flag
        elif deviceFound == 0 and roomFound == 0:
            room['devicesList'].remove(device)
            dateTimeObj = datetime.now()
            currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second}"
            catalog['lastUpdate'] = currentTime
            room['lastUpdate'] = currentTime
            flag = 0
            return catalog, flag

    def __searchByID(self, room, deviceID):
        deviceFound = 1
        for device in room['devicesList']:
            if device['deviceID'] == deviceID:
                deviceFound = 0
                return device, deviceFound

        device = []
        return device, deviceFound

    def changeTopic(self, catalog, newTopic, roomID, deviceID):
        ###############################
        # Returned flags#
        # 2 ---> if room is found device IS NOT FOUND
        # 3 ---> room IS NOT FOUND
        # 0 ---> if room is found device is found
        ###############################
        # {"topic": ["MySmartThingy/1/temp","MySmartThingy/1/hum"]}
        for room in catalog['roomList']:
            if room['roomID'] == roomID:
                device, deviceFound = self.__searchByID(room, deviceID)
                if deviceFound == 1:
                    # intero che viene usato nella classe a livello
                    # superiore per identificare l'errore
                    flag = 2
                    return catalog, flag
                else:
                    for service in device['servicesDetails']:
                        if service["serviceType"] == "MQTT":
                            service['topic'] = newTopic['topic']
                            dateTimeObj = datetime.now()
                            currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second}"
                            room['lastUpdate'] = currentTime
                            catalog['lastUpdate'] = currentTime
                            device['lastUpdate'] = currentTime
                    flag = 0
                    return catalog, flag
        flag = 3
        return catalog, flag

    def changeMeasureType(self, catalog, newType, roomID, deviceID):
        ###############################
        # Returned flags#
        # 2 ---> if room is found device IS NOT FOUND
        # 3 ---> room IS NOT FOUND
        # 0 ---> if room is found device is found
        ###############################
        # {"measureType":"Celsius"}
        for room in catalog['roomList']:
            if room['roomID'] == roomID:
                device, deviceFound = self.__searchByID(room, deviceID)
                if deviceFound == 1:
                    # intero che viene usato nella classe a livello
                    # superiore per identificare l'errore
                    flag = 2
                    return catalog, flag
                else:
                    device['measureType'] = newType['measureType']
                    dateTimeObj = datetime.now()
                    currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second}"
                    room['lastUpdate'] = currentTime
                    catalog['lastUpdate'] = currentTime
                    device['lastUpdate'] = currentTime
                    flag = 0
                    return catalog, flag

        flag = 3
        return catalog, flag

    def updateDeviceName(self, catalog, newName, roomID, deviceID):
        ###############################
        # Returned flags#
        # 2 ---> if room is found device IS NOT FOUND
        # 3 ---> room IS NOT FOUND
        # 0 ---> if room is found device is found
        ###############################
        # {"deviceName":"Pippo"}
        for room in catalog['roomList']:
            if room['roomID'] == roomID:
                device, deviceFound = self.__searchByID(room, deviceID)
                if deviceFound == 1:
                    # intero che viene usato nella classe a livello
                    # superiore per identificare l'errore
                    flag = 2
                    return catalog, flag
                else:
                    device['deviceName'] = newName['deviceName']
                    dateTimeObj = datetime.now()
                    currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second}"
                    room['lastUpdate'] = currentTime
                    catalog['lastUpdate'] = currentTime
                    device['lastUpdate'] = currentTime
                    flag = 0
                    return catalog, flag

        flag = 3
        return catalog, flag


    def changeServiceDetails(self, catalog, newServiceDetails, roomID, deviceID):
        ###############################
        # Returned flags#
        # 2 ---> if room is found device IS NOT FOUND
        # 3 ---> room IS NOT FOUND
        # 0 ---> if room is found device is found
        ###############################
        # {"servicesDetails": [
        #     {   "serviceType": "MQTT",
        #         "serviceIP": "mqtt.eclipse.org",
        #         "topic": [
        #             "MySmartThingy/1/temp",
        #             "MySmartThingy/1/hum" ]},
        #       {  "serviceType": "REST",
        #         "serviceIP": "dht11.org:8080",
        #         "topic": [] }
        #         ] , "allServices" : True/False, "deleteAddAction": 1 }
        # ----------------------------------------------
        # "deleteAddAction":
        # 0 --> Delete service
        # 1 --> Update existing Service
        # ----------------------------------------------
        # "allServices":
        # True  --> Change all services
        # False --> Change not all services
        # ----------------------------------------------
        # {"servicesDetails":[{"serviceType": "MQTT" }],
        #   "allServices" : False, "deleteAddAction": 0 }

        allServices = newServiceDetails['allServices']
        deleteAddAction = newServiceDetails['deleteAddAction']

        for room in catalog['roomList']:
            if room['roomID'] == roomID:
                device, deviceFound = self.__searchByID(room, deviceID)
                if deviceFound == 1:
                    # intero che viene usato nella classe a livello
                    # superiore per identificare l'errore
                    flag = 2
                    return catalog, flag
                else:
                    if allServices and deleteAddAction == 1:
                        device['servicesDetails'] = newServiceDetails['servicesDetails']
                        newServiceType = []
                        for service in device['servicesDetails']:
                            newServiceType.append(service['serviceType'])
                        not_contained_elements = [
                            elem for elem in newServiceType if elem not in device['availableServices']]
                        device['availableServices'].extend(not_contained_elements)
                    elif not allServices and deleteAddAction == 1:
                        device['servicesDetails'].append(
                            newServiceDetails['servicesDetails'])
                        newServiceType = []
                        for service in device['servicesDetails']:
                            newServiceType.append(service['serviceType'])
                        not_contained_elements = [
                            elem for elem in newServiceType if elem not in device['availableServices']]
                        device['availableServices'].extend(not_contained_elements)

                    elif not allServices and deleteAddAction == 0:
                        for service in device['servicesDetails']:
                            if service['serviceType'] == newServiceDetails['serviceType']:
                                device['servicesDetails'].remove(service)
                                device['availableServices'].remove(
                                    newServiceDetails['serviceType'])

                    dateTimeObj = datetime.now()
                    currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second}"
                    room['lastUpdate'] = currentTime
                    catalog['lastUpdate'] = currentTime
                    device['lastUpdate'] = currentTime

        flag = 3
        return catalog, flag

    def updateTSGetInfos(self,catalog, newTSget, roomID, deviceID):
        ###############################
        # Returned flags#
        # 2 ---> if room is found device IS NOT FOUND
        # 3 ---> room IS NOT FOUND
        # 0 ---> if room is found device is found
        ###############################
        # [{"API_key":"S6ULMDXZPCVFBR0H ", "URL":"https://api.thingspeak.com/..."},...]
        for room in catalog['roomList']:
            if room['roomID'] == roomID:
                device, deviceFound = self.__searchByID(room, deviceID)
                if deviceFound == 1:
                    # intero che viene usato nella classe a livello
                    # superiore per identificare l'errore
                    flag = 2
                    return catalog, flag
                else:
                    ThingSpeak = device['ThingSpeak']
                    GetInfos = ThingSpeak['Get_infos']
                    for info in newTSget:
                        GetInfos.append(info)

                    dateTimeObj = datetime.now()
                    currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second}"
                    room['lastUpdate'] = currentTime
                    catalog['lastUpdate'] = currentTime
                    device['lastUpdate'] = currentTime
                    flag = 0
                    return catalog, flag
        flag = 3
        return catalog, flag

    def updateTSPostInfos(self,catalog, newTSPost, roomID, deviceID):
        ###############################
        # Returned flags#
        # 2 ---> if room is found device IS NOT FOUND
        # 3 ---> room IS NOT FOUND
        # 0 ---> if room is found device is found
        ###############################
        # [{"API_key":"S6ULMDXZPCVFBR0H ", "URL":"https://api.thingspeak.com/..."},...]
        for room in catalog['roomList']:
            if room['roomID'] == roomID:
                device, deviceFound = self.__searchByID(room, deviceID)
                if deviceFound == 1:
                    # intero che viene usato nella classe a livello
                    # superiore per identificare l'errore
                    flag = 2
                    return catalog, flag
                else:
                    ThingSpeak = device['ThingSpeak']
                    PostInfos = ThingSpeak['Post_infos']
                    for info in newTSPost:
                        PostInfos.append(info)

                    dateTimeObj = datetime.now()
                    currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second}"
                    room['lastUpdate'] = currentTime
                    catalog['lastUpdate'] = currentTime
                    device['lastUpdate'] = currentTime
                    flag = 0
                    return catalog, flag
        flag = 3
        return catalog, flag
    def getTS_utilities(self,catalog, roomID, deviceID):
        ###############################
        # Returned flags#
        # 2 ---> if room is found device IS NOT FOUND
        # 3 ---> room IS NOT FOUND
        # 0 ---> if room is found device is found
        ###############################
        data = {}
        for room in catalog['roomList']:
            if room['roomID'] == roomID:
                device, deviceFound = self.__searchByID(room, deviceID)
                if deviceFound == 1:
                    # intero che viene usato nella classe a livello
                    # superiore per identificare l'errore
                    flag = 2
                    return data, flag
                else:
                    flag = 0
                    data=device['ThingSpeak']
                    return data, flag
        flag = 3
        return data, flag

    def updateChannelID(self,catalog, newChannel, roomID, deviceID):
        ###############################
        # Returned flags#
        # 2 ---> if room is found device IS NOT FOUND
        # 3 ---> room IS NOT FOUND
        # 0 ---> if room is found device is found
        ###############################
        # {"channelID":..... }
        for room in catalog['roomList']:
            if room['roomID'] == roomID:
                device, deviceFound = self.__searchByID(room, deviceID)
                if deviceFound == 1:
                    # intero che viene usato nella classe a livello
                    # superiore per identificare l'errore
                    flag = 2
                    return catalog, flag
                else:
                    ThingSpeak = device['ThingSpeak']
                    ThingSpeak['channelID'] = newChannel
                    dateTimeObj = datetime.now()
                    currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second}"
                    room['lastUpdate'] = currentTime
                    catalog['lastUpdate'] = currentTime
                    device['lastUpdate'] = currentTime
                    flag = 0
                    return catalog, flag
        flag = 3
        return catalog, flag

