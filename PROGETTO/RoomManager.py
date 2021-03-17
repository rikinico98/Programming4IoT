from datetime import datetime


class RoomManager:
    def __init__(self):
        pass

    def findRoomType(self, catalog, roomID):

        ###############################
        # Returned flags#
        # 3 ---> room IS NOT FOUND
        # 0 ---> TUTTO E' ANDATO BENE
        ###############################
        room, roomFound = self.__searchByID(catalog['roomList'], roomID)
        if roomFound == 1:
            roomType = ""
            flag = 3
            return roomType, flag
        else:
            roomType = room['product_type']
            flag = 0
            return roomType, flag

    def addNewRoom(self, catalog, newRoom, roomID):
        ###############################
        # Returned flags#
        # 3 ---> room IS NOT FOUND
        # 0 ---> room FOUND
        ###############################
        user, roomFound = self.__searchByID(catalog['roomList'], roomID)
        if roomFound == 0:
            flag = 0
            return catalog, flag
        else:
            flag = 3
            dateTimeObj = datetime.now()
            currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second}"
            catalog['lastUpdate'] = currentTime
            for device in newRoom["devicesList"]:
                device['lastUpdate'] = currentTime
            ranges = dict(Temperature=newRoom['ranges']['Temperature'],
                          Humidity=newRoom['ranges']['Humidity'],
                          Smoke=newRoom['ranges']['Smoke'])
            ThingSpeak = newRoom['ThingSpeak']
            catalog['roomList'].append(
                dict(
                    roomID=roomID,
                    devicesList=newRoom["devicesList"],
                    product_type=newRoom["product_type"],
                    ThingSpeak={
                        "channelID": ThingSpeak['channelID'],
                        "api_key_read": ThingSpeak['api_key_read'],
                        "api_key_write": ThingSpeak['api_key_write']},
                    ranges=ranges,
                    lastUpdate=currentTime))
            return catalog, flag

    def deleteRoom(self, catalog, roomID):

        ###############################
        # Returned flags#
        # 3 ---> room IS NOT FOUND
        # 0 ---> TUTTO E' ANDATO BENE
        ###############################
        room, roomFound = self.__searchByID(catalog['roomList'], roomID)
        if roomFound == 1:
            flag = 3
            return catalog, flag
        else:
            flag = 0
            catalog['roomList'].remove(room)
            dateTimeObj = datetime.now()
            currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second}"
            catalog['lastUpdate'] = currentTime
            return catalog, flag

    def __searchByID(self, roomList, roomID):
        roomFound = 1
        for room in roomList:
            if room['roomID'] == roomID:
                roomFound = 0
                return room, roomFound

        room = []
        return room, roomFound

    def changeProductType(self, catalog, newProductType, roomID):

        ###############################
        # Returned flags#
        # 3 ---> room IS NOT FOUND
        # 0 ---> TUTTO E' ANDATO BENE
        ###############################
        # newProductType=  {"product_type": "00"}
        room, roomFound = self.__searchByID(catalog['roomList'], roomID)
        if roomFound == 1:
            flag = 3
            return catalog, flag
        else:
            room['product_type'] = newProductType['product_type']
            dateTimeObj = datetime.now()
            currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second}"
            room['lastUpdate'] = currentTime
            catalog['lastUpdate'] = currentTime
            flag = 0
            return catalog, flag

    def findSameMeasureID(self, catalog, roomID, measureType):

        ###############################
        # Returned flags#
        # 3 ---> room IS NOT FOUND
        # 0 ---> TUTTO E' ANDATO BENE
        ###############################
        foundDeviceIds = []

        room, roomFound = self.__searchByID(catalog['roomList'], roomID)
        if roomFound == 1:
            flag = 3
            return foundDeviceIds, flag
        else:
            for device in room['devicesList']:
                if device["measureType"] == measureType:
                    foundDeviceIds.append(device['deviceID'])
            flag = 0
            return foundDeviceIds, flag

    def getTS_utilities(self, catalog, roomID):
        ###############################
        # Returned flags#
        # 3 ---> room IS NOT FOUND
        # 0 ---> TUTTO E' ANDATO BENE
        ###############################
        data = {}
        room, roomFound = self.__searchByID(catalog['roomList'], roomID)
        if roomFound == 1:
            data = {}
            flag = 3
            return data, flag
        else:
            data = room['ThingSpeak']
            flag = 0
            return data, flag

    def updateChannelID(self, catalog, newChannel, roomID):

        ###############################
        # Returned flags#
        # 3 ---> room IS NOT FOUND
        # 0 ---> TUTTO E' ANDATO BENE
        ###############################
        # {“channelID”: 134252}
        room, roomFound = self.__searchByID(catalog['roomList'], roomID)
        if roomFound == 1:
            flag = 3
            return catalog, flag
        else:
            ThingSpeak = room['ThingSpeak']
            ThingSpeak['channelID'] = newChannel['channelID']
            dateTimeObj = datetime.now()
            currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second}"
            room['lastUpdate'] = currentTime
            catalog['lastUpdate'] = currentTime
            flag = 0
            return catalog, flag

    def updateTSPostInfos(self, catalog, newApi, roomID):

        ###############################
        # Returned flags#
        # 3 ---> room IS NOT FOUND
        # 0 ---> TUTTO E' ANDATO BENE
        ###############################
        # {“api_key_write”: S6ULMDXZPCVFBR0H}
        room, roomFound = self.__searchByID(catalog['roomList'], roomID)
        if roomFound == 1:
            flag = 3
            return catalog, flag
        else:
            ThingSpeak = room['ThingSpeak']
            ThingSpeak['channelID'] = newApi['api_key_write']
            dateTimeObj = datetime.now()
            currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second}"
            room['lastUpdate'] = currentTime
            catalog['lastUpdate'] = currentTime
            flag = 0
            return catalog, flag

    def updateTSGetInfos(self, catalog, newApi, roomID):

        ###############################
        # Returned flags#
        # 3 ---> room IS NOT FOUND
        # 0 ---> TUTTO E' ANDATO BENE
        ###############################
        # {“api_key_read”: ZVBAO2QDON8B19X0}

        room, roomFound = self.__searchByID(catalog['roomList'], roomID)
        if roomFound == 1:
            flag = 3
            return catalog, flag
        else:
            ThingSpeak = room['ThingSpeak']
            ThingSpeak['channelID'] = newApi['api_key_read']
            dateTimeObj = datetime.now()
            currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second}"
            room['lastUpdate'] = currentTime
            catalog['lastUpdate'] = currentTime
            flag = 0
            return catalog, flag

    def updateRanges(self, catalog, newRanges, roomID):

        ###############################
        # Returned flags#
        # 3 ---> room IS NOT FOUND
        # 0 ---> TUTTO E' ANDATO BENE
        ###############################
        # {"ranges":{"Temperature":[0,0],"Humidity":[0,0],"Smoke":[0,0]}}
        # NON PER FORZA DEVO AGGIORNARE TUTTI I RANGE IL CAMBIAMENTO PARZIALE
        # E' PREVISTO
        room, roomFound = self.__searchByID(catalog['roomList'], roomID)
        if roomFound == 1:
            flag = 3
            return catalog, flag
        else:
            rangesDict=newRanges['ranges']
            ranges=room['ranges']
            keyList=list(rangesDict.keys())
            if ("Temperature" in keyList):
                ranges['Temperature']=rangesDict['Temperature']
            if ("Humidity" in keyList):
                ranges['Humidity'] = rangesDict['Humidity']
            if ("Smoke" in keyList):
                ranges['Smoke'] = rangesDict['Smoke']
            dateTimeObj = datetime.now()
            currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second}"
            room['lastUpdate'] = currentTime
            catalog['lastUpdate'] = currentTime
            flag = 0
            return catalog, flag
        pass
