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
    def findRole(self, catalog, userID):

        ###############################
        # Returned flags#
        # 1 ---> user IS NOT FOUND
        # 0 ---> TUTTO E' ANDATO BENE
        ###############################
        user, userFound = self.__searchByID(catalog['userList'], userID)
        if userFound == 1:
            role = ""
            flag = 1
            return role, flag
        else:
            role = user['role']
            flag = 0
            return role, flag

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
                    role=newUser["role"],
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

    def updateRole(self, catalog, newUser, userID):
        ###############################
        # Returned flags#
        # 1 ---> user IS NOT FOUND
        # 0 ---> user FOUND
        ###############################
        # {"role": "nuovo_ruolo"}
        user, userFound = self.__searchByID(catalog['userList'], userID)
        if userFound == 0:
            user['role'] = newUser['role']
            dateTimeObj = datetime.now()
            currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second}"
            catalog['lastUpdate'] = currentTime
            return catalog, userFound
        else:
            return catalog, userFound

    def updateAssignedRooms(self, catalog, newRooms, userID):
        ###############################
        # Returned flags#
        # 1 ---> user IS NOT FOUND
        # 0 ---> user FOUND
        ###############################
        # newRooms = [{"roomID":"R_001","action":0},{"roomID":"R_011","action":1}]
        user, userFound = self.__searchByID(catalog['userList'], userID)
        if userFound == 0:
            for roomID in user["roomIDs"]:
                for newID in newRooms:
                    # controllo se il flag è uguale a 0 e se il nuovo id che sto analizzando
                    # è contenuto nella lista di id vecchi
                    if roomID == newID['roomID'] and newID['action'] == 0:
                        # se lo trovo rimuovo l'ID dai vecchi ID
                        user["roomIDs"].remove(newID['roomID'])
                        # se l'azione va a buon fine metto il flag=2 per ignorare questo
                        # ID nelle prossime iterazioni
                        newID['action'] = 2
                    elif newID['action'] != 2:
                        # se non lo trovo e il nuovo ID non è ancora stato analizzato
                        # aggiungo il nuov id alla lista
                        user["roomIDs"].append(newID['roomID'])
                        newID['action'] = 2
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
