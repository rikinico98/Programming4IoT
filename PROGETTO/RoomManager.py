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
            catalog['roomList'].append(
                dict(
                    roomID=roomID,
                    devicesList=newRoom["devicesList"],
                    product_type=newRoom["product_type"],
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
            room['lastUpdate']=currentTime
            catalog['lastUpdate'] = currentTime
            flag = 0
            return catalog, flag
