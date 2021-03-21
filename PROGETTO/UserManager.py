from datetime import datetime


class UserManager:
    def __init__(self):
        pass

    def findRoomAssigned(self, catalog, userID):

        ###############################
        # Returned flags#
        # 1 ---> user IS NOT FOUND
        # 0 ---> TUTTO E' ANDATO BENE
        ###############################
        user, userFound = self.__searchByID(catalog['userList'], userID)
        if userFound == 1:
            assignedRoomIDs = ""
            flag = 1
            return assignedRoomIDs, flag
        else:
            assignedRoomIDs = user['roomIDs']
            flag = 0
            return assignedRoomIDs, flag
    def findChatID(self, catalog, userID):

        ###############################
        # Returned flags#
        # 1 ---> user IS NOT FOUND
        # 0 ---> TUTTO E' ANDATO BENE
        ###############################
        user, userFound = self.__searchByID(catalog['userList'], userID)
        if userFound == 1:
            chatID = ""
            flag = 1
            return chatID, flag
        else:
            chatID = user['chatID']
            flag = 0
            return chatID, flag

    def addNewUser(self, catalog, newUser, userID):
        ###############################
        # Returned flags#
        # 1 ---> user IS NOT FOUND
        # 0 ---> user FOUND
        ###############################
        user, userFound = self.__searchByID(catalog['userList'], userID)
        if userFound == 0:
            return catalog, userFound
        else:
            dateTimeObj = datetime.now()
            currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second}"
            catalog['lastUpdate'] = currentTime
            catalog['userList'].append(
                dict(
                    userID=userID,
                    chatID=None,
                    roomIDs=newUser["roomIDs"]))
            return catalog, userFound

    def deleteUser(self, catalog, userID):
        ###############################
        # Returned flags#
        # 1 ---> user IS NOT FOUND
        # 0 ---> TUTTO E' ANDATO BENE
        ###############################
        user, userFound = self.__searchByID(catalog['userList'], userID)
        if userFound == 1:
            flag = 1
            return catalog, flag
        else:
            flag = 0
            catalog['userList'].remove(user)
            dateTimeObj = datetime.now()
            currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second}"
            catalog['lastUpdate'] = currentTime
            return catalog, flag

    def updateChatID(self, catalog, updateChatID, userID):
        ###############################
        # Returned flags#
        # 1 ---> user IS NOT FOUND
        # 0 ---> user FOUND
        ###############################
        # {"chatID": "nuovo_chatID"}
        user, userFound = self.__searchByID(catalog['userList'], userID)
        if userFound == 0:
            user['chatID'] = newUser['chatID']
            dateTimeObj = datetime.now()
            currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second}"
            catalog['lastUpdate'] = currentTime
            return catalog, userFound
        else:
            return catalog, userFound

    def addAssignedRooms(self, catalog, newRooms, userID):
        ###############################
        # Returned flags#
        # 1 ---> user IS NOT FOUND
        # 0 ---> user FOUND
        ###############################
        # {"roomIDs":["R_001,"R_011"]}
        user, userFound = self.__searchByID(catalog['userList'], userID)
        if userFound == 0:
            for newID in newRooms['roomIDs']:
                if newID not in user["roomIDs"]:
                    user["roomIDs"].append(newID)
            dateTimeObj = datetime.now()
            currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second}"
            catalog['lastUpdate'] = currentTime

            return catalog, userFound
        else:
            return catalog, userFound
    def deleteAssignedRooms(self, catalog, newRooms, userID):
        ###############################
        # Returned flags#
        # 1 ---> user IS NOT FOUND
        # 0 ---> user FOUND
        ###############################
        # {"roomIDs":["R_001,"R_011"]}
        user, userFound = self.__searchByID(catalog['userList'], userID)
        if userFound == 0:
            for roomID in user["roomIDs"]:
                for newID in newRooms['roomIDs']:
                    # controllo  se il nuovo id che sto analizzando
                    # è contenuto nella lista di id vecchi
                    if roomID == newID:
                        # se lo trovo rimuovo l'ID dai vecchi ID
                        user["roomIDs"].remove(newID)

            dateTimeObj = datetime.now()
            currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second}"
            catalog['lastUpdate'] = currentTime

            return catalog, userFound
        else:
            return catalog, userFound

    def __searchByID(self, userList, userID):
        userFound = 1
        for user in userList:
            if user['userID'] == userID:
                userFound = 0
                return user, userFound

        user = []
        return user, userFound
    def updateRole(self, catalog, newChatID, userID):
        ###############################
        # Returned flags#
        # 1 ---> user IS NOT FOUND
        # 0 ---> user FOUND
        ###############################
        # {"userID": "nuovo_userID"}
        user, userFound = self.__searchByID(catalog['userList'], userID)
        if userFound == 0:
            user['userID'] = newUser['userID']
            dateTimeObj = datetime.now()
            currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second}"
            catalog['lastUpdate'] = currentTime
            return catalog, userFound
        else:
            return catalog, userFound
