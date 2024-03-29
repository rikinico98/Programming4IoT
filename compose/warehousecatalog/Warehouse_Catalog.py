import cherrypy
import DeviceManager as dm
import UserManager as um
import RoomManager as rm
from datetime import datetime
import json


class WareHouse_Catalog:
    exposed = True

    def __init__(self, Settings):
        dateTimeObj = datetime.now()
        currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second} "
        self.catalog = {
            "projectOwner": ['Lazzarini Ilaria',
                             'Lia Caterina',
                             'Nicolicchia Riccardo',
                             'Vigliotti Manuela'],
            "projectName": "WareHouse Manager",
            "lastUpdate": currentTime,
            "roomList": [],
            "userList": [],
            "MQTT_utilities":{
                "msgBroker": Settings['msgBroker'],
                "port": Settings['port_MQTT'],
                "mqttTopicGeneral": Settings['mqttTopicGeneral']
            },
            "Thingspeak_API": {
                "api_key_thingspeak": Settings['api_key_thingspeak'],
                "clientID_Thingspeak_MQTT": Settings['clientID_Thingspeak_MQTT'],
                "mqttTopicThingspeak": Settings['mqttTopicThingspeak']

            },
            "Telegram_utilities":{
                        "telegramToken": Settings['telegramToken'],
                        "brokerURL": Settings['msgBroker'],
                        "brokerPort": Settings['port_MQTT'],
                        "clientID_MQTT":Settings['clientID_Telegram_MQTT'],
                        "mqttTopic":Settings['mqttTopicTelegram']
            },
            "service_comm_port":{
                "port_catalog": Settings['port_catalog'],
                "port_form": Settings['port_form'],
                "port_storedProducts": Settings['port_storedProducts'],
                "port_databaseStats": Settings['port_databaseStats'],
                "port_soldProducts": Settings['port_soldProducts'],
                "port_dm":Settings['port_dm']

            },
            "URL":{
                "catalogURL": Settings['catalogURL'],
                "databaseStatsURL": Settings['databaseStatsURL'],
                "storedProductsURL": Settings['storedProductsURL'],
                "soldProductsURL": Settings['soldProductsURL'],
                "formURL": Settings['formURL'],
                "dmURL":Settings['dmURL']

            }

        }
        self.DeviceManager = dm.DeviceManager()
        self.UserManager = um.UserManager()
        self.RoomManager = rm.RoomManager()

##########################################################################
        # impostare la richiesta REST in modo tale da avere
        # section/dato_da_modificare_o_cambiare oppure
        # section/subsection/azione
        # GET
        # catalog/msg_broker
        # catalog/
        #
        # catalog/ID_stanza/ID_Device/topic
        # catalog/ID_utente/assigned_rooms
        # catalog/ID_stanza/assigned_product_type
        # catalog/ID_utente/chatID
        # catalog/ID_stanza/users
        # catalog/ID_stanza/measure_type/TIPO_DI_MISURA
        # catalog/ID_stanza/TS_utilities
        # catalog/ID_stanza/ranges

        # POST
        # catalog/ID_stanza/ID_device/new
        # catalog/ID_utente/new
        # catalog/ID_stanza/new
        # PUT
        # catalog/ID_stanza/ID_device/update_name
        # catalog/ID_stanza/ID_device/change_meas_type
        # catalog/ID_stanza/ID_device/add_service_details
        # catalog/ID_stanza/ID_device/change_topic
        # ctalog/ID_stanza/ID_device/update_timestamp
        # catalog/ID_utente/change_chatID
        # catalog/ID_utente/change_role
        # catalog/ID_utente/add_assigned_rooms
        # catalog/ID_stanza/change_product_type
        # catalog/ID_stanza/change_ranges
        # catalog/ID_stanza/TS_channel
        # catalog/ID_stanza/TS_get
        # catalog/ID_stanza/TS_post
        # DELETE
        # catalog/ID_stanza/ID_device/delete
        # catalog/ID_utente/delete
        # catalog/ID_stanza/delete
        # catalog/ID_stanza/ID_device/delete_service_details/TIPO_DI_SERVIZIO
        # catalog/ID_utente/delete_assigned_rooms

##########################################################################
    def GET(self, *uri):
        cond1 = (len(uri) != 0)
        if cond1:
            # acquisire la sezione in questo caso riferita al catalog
            # controllare se è una richiesta riferita a una delle tre sotto
            # sezioni: Room, Device o Users
            if len(uri) > 2:
                # sotto sezione di riferimento
                IDReference = uri[1]
                # controllare il prefisso per capire a quale sotto sezione si
                # riferisce
                ID_type = IDReference[0:2]
                if ID_type.upper() == 'U_' or ID_type.upper() == 'M_':
                    # controllare a quale azione riguardo gli utenti si
                    # riferisce
                    userID = IDReference
                    cmd = uri[2]
                    if cmd == 'assigned_rooms':
                        assignedRoomIDs, flag = self.UserManager.findRoomAssigned(
                            self.catalog, userID)
                        if flag == 0:
                            result = dict(assignedRoomIds=assignedRoomIDs)
                            jsonOut = json.dumps(result)
                            return jsonOut
                        elif flag == 1:
                            raise cherrypy.HTTPError(507, "User not found")
                    if cmd == 'chatID':
                        chatID, flag = self.UserManager.findChatID(
                            self.catalog, userID)
                        if flag == 0:
                            result = dict(chatID=chatID)
                            jsonOut = json.dumps(result)
                            return jsonOut
                        elif flag == 1:
                            raise cherrypy.HTTPError(507, "User not found")

                elif ID_type.upper() == 'R_':
                    # controllare se è un'azione riferita alle camere o a un
                    # device
                    if len(uri) > 3:
                        # controllare a quale azione riguardo i device si
                        # riferisce
                        roomID = IDReference
                        deviceID = uri[2]
                        cmd = uri[3]
                        ID_type2 = deviceID[0:2]
                        if ID_type2.upper() == 'D_':
                            # restituzione del topic
                            if cmd == 'topic':
                                # TOPIC E' UNA LISTAAAA
                                data, flag = self.DeviceManager.findTopic(
                                    self.catalog, roomID, deviceID)
                                result = dict(topic=data)
                            elif cmd == 'get_field':
                                data, flag = self.DeviceManager.get_field(
                                    self.catalog, roomID, deviceID)
                                result = dict(field=data)

                            else:
                                raise cherrypy.HTTPError(
                                    401, "Unexpected command - Wrong Command ")
                            if flag == 0:
                                jsonOut = json.dumps(result)
                                return jsonOut
                            elif flag == 2:
                                raise cherrypy.HTTPError(
                                    505, "Device not found")
                            elif flag == 3:
                                raise cherrypy.HTTPError(
                                    506, "Room not found")
                        elif uri[2] == 'measure_type':
                            # E' una lista l'output
                            measureType = uri[3]
                            data, flag = self.RoomManager.findSameMeasureID(
                                self.catalog, roomID, measureType)
                            result = dict(foundIDs=data)
                            if flag == 0:
                                jsonOut = json.dumps(result)
                                return jsonOut
                            elif flag == 3:
                                raise cherrypy.HTTPError(506, "Room not found")

                        else:
                            raise cherrypy.HTTPError(
                                400, "Unexpected command - ID NOT CLASSIFIED ")

                    else:
                        # controllare a quale azione riguardo le stanze si
                        # riferisce
                        roomID = IDReference
                        cmd = uri[2]

                        if cmd == 'assigned_product_type':
                            product_type, flag = self.RoomManager.findRoomType(
                                self.catalog, roomID)
                            result = dict(product_type=product_type)
                        elif cmd == 'TS_utilities':
                            # Output che da:
                            # { ThingSpeak: {“channelID”: 134252, “api_key_read”: ZVBAO2QDON8B19X0,
                            # “api_key_write”: S6ULMDXZPCVFBR0H}}
                            data, flag = self.RoomManager.getTS_utilities(
                                self.catalog, roomID)
                            result = dict(ThingSpeak=data)
                        elif cmd=='ranges':
                            data, flag = self.RoomManager.getRanges(
                                self.catalog, roomID)
                            result = dict(ranges=data)
                        elif cmd=='users':
                            data, flag = self.RoomManager.getUsers(
                                self.catalog, roomID)
                            result = dict(user=data)
                        elif cmd=='devices':
                            print('ciao')
                            data, flag = self.RoomManager.getDevices(
                                self.catalog, roomID)
                            result = dict(devices=data)

                        else:
                            raise cherrypy.HTTPError(
                                401, "Unexpected command - Wrong Command ")

                        if flag == 0:
                            jsonOut = json.dumps(result)
                            return jsonOut
                        elif flag == 3:
                            raise cherrypy.HTTPError(506, "Room not found")
                        elif flag==4:
                            raise cherrypy.HTTPError(506, "User not found")

                else:
                    raise cherrypy.HTTPError(
                        400, "Unexpected command - ID NOT CLASSIFIED ")

            else:
                # dato richiesto
                cmd = uri[1]
                # "MQTT_utilities": {
                #     "msgBroker":
                #     "port":
                #     "mqttTopicGeneral":
                # }
                if cmd == 'MQTT_utilities':
                    # controllare se il msg broker è stato definito
                    MQTT_utilities=self.catalog['MQTT_utilities']
                    if MQTT_utilities['port'] == '':
                        raise cherrypy.HTTPError(501, "Port not defined")
                    if MQTT_utilities['msgBroker'] == '':
                        raise cherrypy.HTTPError(500, "Msg Broker not defined")
                    result = dict(MQTT_utilities=self.catalog['MQTT_utilities'])
                    jsonOut = json.dumps(result)
                    return jsonOut

                # "Telegram_utilities": {
                #     "telegramToken":
                #     "brokerIP":
                #     "brokerPort":
                #     "clientID_MQTT":
                #     "mqttTopic":
                # }
                elif cmd== 'Telegram':
                    result = dict(Telegram=self.catalog['Telegram_utilities'])
                    jsonOut = json.dumps(result)
                    return jsonOut

                # "Thingspeak_API": {
                #     "api_key_thingspeak":
                #     "clientID_Thingspeak_MQTT":
                #     "mqttTopicThingspeak":
                #
                # }
                elif cmd== 'Thingspeak_API':
                    result = dict(Thingspeak_API=self.catalog['Thingspeak_API'])
                    jsonOut = json.dumps(result)
                    return jsonOut

                # "service_comm_port": {
                #     "port_catalog":
                #     "port_form":
                #     "port_storedProducts":
                #     "port_databaseStats":
                #     "port_soldProducts":
                #
                # }
                elif cmd== 'service_comm_port':
                    result = dict(service_comm_port=self.catalog['service_comm_port'])
                    jsonOut = json.dumps(result)
                    return jsonOut

                # "URL": {
                #     "catalogURL":
                #     "databaseStatsURL":
                #     "storedProductsURL":
                #     "soldProductsURL":
                #     "formURL":
                #
                # }
                elif cmd== 'URL':
                    result = dict(URL=self.catalog['URL'])
                    jsonOut = json.dumps(result)
                    return jsonOut

                elif cmd == 'users':
                    # controllare se la porta è stata definita in maniera
                    # corretta
                    if self.catalog['userList'] == []:
                        raise cherrypy.HTTPError(509, "User list not defined")
                    result = dict(userList=self.catalog['userList'])
                    jsonOut = json.dumps(result)
                    return jsonOut
                elif cmd == 'rooms':
                    # controllare se la porta è stata definita in maniera
                    # corretta
                    if self.catalog['roomList'] == []:
                        raise cherrypy.HTTPError(508, "Room list not defined")
                    result = dict(roomList=self.catalog['roomList'])
                    jsonOut = json.dumps(result)
                    return jsonOut

    def POST(self, *uri):

        body = cherrypy.request.body.read()
        jsonBody = json.loads(body)
        # controllare se è una richiesta riferita a una delle tre sotto
        # sezioni: Room, Device o Users
        if len(uri) > 2:
            # sotto sezione di riferimento
            IDReference = uri[1]
            # controllare il prefisso per capire a quale sotto sezione si
            # riferisce
            ID_type = IDReference[0:2]
            if ID_type.upper() == 'U_' or ID_type.upper() == 'M_':
                # controllare a quale azione riguardo gli utenti si riferisce
                userID = IDReference
                cmd = uri[2]
                if cmd == 'new':
                    newUser = jsonBody
                    self.catalog, flag = self.UserManager.addNewUser(
                        self.catalog, newUser, userID)
                    if flag == 0:
                        raise cherrypy.HTTPError(402, "User NOT UNIQUE ID")
                    else:
                        contents = json.dumps(self.catalog)
                        return contents
                else:
                    raise cherrypy.HTTPError(
                        401, "Unexpected command - Wrong Command ")

            elif ID_type.upper() == 'R_':
                # controllare se è un'azione riferita alle camere o a un device
                if len(uri) > 3:
                    # controllare a quale azione riguardo i device si riferisce
                    roomID = IDReference
                    deviceID = uri[2]
                    cmd = uri[3]
                    ID_type2 = deviceID[0:2]
                    if ID_type2.upper() == 'D_':
                        if cmd == 'new':
                            newDevice = jsonBody
                            self.catalog, flag = self.DeviceManager.addNewDevice(
                                self.catalog, newDevice, roomID, deviceID)
                            if flag == 2:
                                raise cherrypy.HTTPError(
                                    403, "Device NOT UNIQUE ID")
                            elif flag == 0:
                                contents = json.dumps(self.catalog)
                                return contents
                            elif flag == 3:
                                raise cherrypy.HTTPError(506, "Room not found")
                        else:
                            raise cherrypy.HTTPError(
                                401, "Unexpected command - Wrong Command ")
                    else:
                        raise cherrypy.HTTPError(
                            400, "Unexpected command - ID NOT CLASSIFIED ")

                else:
                    # controllare a quale azione riguardo le stanze si
                    # riferisce
                    roomID = IDReference
                    cmd = uri[2]
                    if cmd == 'new':
                        newRoom = jsonBody
                        self.catalog, flag = self.RoomManager.addNewRoom(
                            self.catalog, newRoom, roomID)
                        if flag == 0:
                            raise cherrypy.HTTPError(404, "Room NOT UNIQUE ID")
                        else:
                            contents = json.dumps(self.catalog)
                            return contents
                    else:
                        raise cherrypy.HTTPError(
                            401, "Unexpected command - Wrong Command ")

            else:
                raise cherrypy.HTTPError(
                    400, "Unexpected command - ID NOT CLASSIFIED ")

    def PUT(self, *uri):

        body = cherrypy.request.body.read()
        jsonBody = json.loads(body)
        # controllare se è una richiesta riferita a una delle tre sotto
        # sezioni: Room, Device o Users
        if len(uri) > 2:
            # sotto sezione di riferimento
            IDReference = uri[1]
            # controllare il prefisso per capire a quale sotto sezione si
            # riferisce
            ID_type = IDReference[0:2]
            if ID_type.upper() == 'U_' or ID_type.upper() == 'M_':
                # controllare a quale azione riguardo gli utenti si riferisce
                userID = IDReference
                cmd = uri[2]
                if cmd == 'change_chatID':
                    # Il messaggio passato nel body contiene solo la key-value pair
                    # {"chatID": "nuovo_chatID"}
                    newChatID = jsonBody
                    self.catalog, flag = self.UserManager.updateChatID(
                        self.catalog, newChatID, userID)
                if cmd == 'change_role':
                    # Il messaggio passato nel body contiene solo la key-value pair
                    # {"userID": "nuovo_userID"}
                    newUserID = jsonBody
                    self.catalog, flag = self.UserManager.updateRole(
                        self.catalog, newUserID, userID)
                elif cmd == 'add_assigned_rooms':
                    # Il messaggio passato nel body contiene solo la lista di stanze:
                    # {"roomIDs":["R_001,"R_011"]}
                    newRooms = jsonBody
                    self.catalog, flag = self.UserManager.addAssignedRooms(
                        self.catalog, newRooms, userID)
                elif cmd == 'delete_assigned_rooms':
                    # Il messaggio passato nel body contiene solo la lista di stanze:
                    # {"roomIDs":["R_001,"R_011"]}
                    newRooms = jsonBody
                    self.catalog, flag = self.UserManager.deleteAssignedRooms(
                        self.catalog, newRooms, userID)
                else:
                    raise cherrypy.HTTPError(
                        401, "Unexpected command - Wrong Command ")
                if flag == 0:
                    contents = json.dumps(self.catalog)
                    return contents
                elif flag == 1:
                    raise cherrypy.HTTPError(507, "User not found")

            elif ID_type.upper() == 'R_':
                # controllare se è un'azione riferita alle camere o a un device
                if len(uri) > 3:
                    # controllare a quale azione riguardo i device si riferisce
                    roomID = IDReference
                    deviceID = uri[2]
                    cmd = uri[3]
                    ID_type2 = deviceID[0:2]
                    if ID_type2.upper() == 'D_':
                        if cmd == 'update_name':
                            # il body del messaggio avrà una forma del tipo
                            # {"deviceName":"Pippo"}
                            newName = jsonBody
                            self.catalog, flag = self.DeviceManager.updateDeviceName(
                                self.catalog, newName, roomID, deviceID)
                        elif cmd == 'change_meas_type':
                            # il body del messaggio avrà una forma del tipo
                            # {"measureType":"Celsius"}
                            newType = jsonBody
                            self.catalog, flag = self.DeviceManager.changeMeasureType(
                                self.catalog, newType, roomID, deviceID)
                        elif cmd == 'add_service_details':
                            # il body del messaggio avrà la forma
                            # {"servicesDetails": [
                            #     {   "serviceType": "MQTT",
                            #         "serviceIP": "mqtt.eclipse.org",
                            #         "topic": [
                            #             "MySmartThingy/1/temp",
                            #             "MySmartThingy/1/hum" ]},
                            #       {  "serviceType": "REST",
                            #         "serviceIP": "dht11.org:8080",
                            #         "topic": [] }
                            #         ] }

                            newServiceDetails = jsonBody
                            self.catalog, flag = self.DeviceManager.addServiceDetails(
                                self.catalog, newServiceDetails, roomID, deviceID)

                        elif cmd == 'change_topic':
                            # il body del messaggio avrà la forma
                            # {"topic": ["MySmartThingy/1/temp","MySmartThingy/1/hum"]}
                            newTopic = jsonBody
                            self.catalog, flag = self.DeviceManager.changeTopic(
                                self.catalog, newTopic, roomID, deviceID)
                        elif cmd == 'change_field':
                            # il body del messaggio avrà la forma
                            # {"field": 'field1'}
                            newField = jsonBody
                            self.catalog, flag = self.DeviceManager.changeField(
                                self.catalog, newField, roomID, deviceID)
                        elif cmd == 'update_timestamp':
                            # il body del messaggio avrà la forma
                            # {"timestamp": new_timestamp_value}
                            newTimestamp = jsonBody["timestamp"]
                            self.catalog, flag = self.DeviceManager.changeTimestamp(
                                self.catalog, newTimestamp, roomID, deviceID)

                        else:
                            raise cherrypy.HTTPError(
                                401, "Unexpected command - Wrong Command ")

                        if flag == 0:
                            contents = json.dumps(self.catalog)
                            return contents
                        elif flag == 2:
                            raise cherrypy.HTTPError(
                                505, "Device not found")
                        elif flag == 3:
                            raise cherrypy.HTTPError(
                                506, "Room not found")
                    else:
                        raise cherrypy.HTTPError(
                            400, "Unexpected command - ID NOT CLASSIFIED ")

                else:
                    # controllare a quale azione riguardo le stanze si
                    # riferisce
                    roomID = IDReference
                    cmd = uri[2]
                    if cmd == 'change_product_type':
                        # il body del messaggio avrà una forma del tipo
                        # {"product_type": "00"}
                        newProductType = jsonBody
                        self.catalog, flag = self.RoomManager.changeProductType(
                            self.catalog, newProductType, roomID)
                    elif cmd == 'TS_channel':
                        # {“channelID”: 134252}
                        newChannel = jsonBody
                        self.catalog, flag = self.RoomManager.updateChannelID(
                            self.catalog, newChannel, roomID)
                    elif cmd == 'change_ranges':
                        # {"ranges":{"Temperature":[0,0],"Humidity":[0,0],"Smoke":[0,0]}}
                        # NON PER FORZA DEVO AGGIORNARE TUTTI I RANGE IL CAMBIAMENTO PARZIALE
                        # E' PREVISTO
                        newRanges = jsonBody
                        self.catalog, flag = self.RoomManager.updateRanges(
                            self.catalog, newRanges, roomID)
                    elif cmd == 'TS_post':
                        # {“api_key_write”: S6ULMDXZPCVFBR0H}
                        newApi = jsonBody
                        self.catalog, flag = self.RoomManager.updateTSPostInfos(
                            self.catalog, newApi, roomID)
                    elif cmd == 'TS_get':
                        # {“api_key_read”: ZVBAO2QDON8B19X0}
                        newApi = jsonBody
                        self.catalog, flag = self.RoomManager.updateTSGetInfos(
                            self.catalog, newApi, roomID)
                    else:
                        raise cherrypy.HTTPError(
                            401, "Unexpected command - Wrong Command ")
                    if flag == 0:
                        contents = json.dumps(self.catalog)
                        return contents
                    elif flag == 3:
                        raise cherrypy.HTTPError(506, "Room not found")

            else:
                raise cherrypy.HTTPError(
                    400, "Unexpected command - ID NOT CLASSIFIED ")

    def DELETE(self, *uri):
        cond1 = (len(uri) != 0)
        if cond1:
            # controllare se è una richiesta riferita a una delle tre sotto
            # sezioni: Room, Device o Users
            if len(uri) > 2:
                # sotto sezione di riferimento
                IDReference = uri[1]
                # controllare il prefisso per capire a quale sotto sezione si
                # riferisce
                ID_type = IDReference[0:2]
                if ID_type.upper() == 'U_' or ID_type.upper() == 'M_':
                    # controllare a quale azione riguardo gli utenti si
                    # riferisce
                    userID = IDReference
                    cmd = uri[2]
                    if cmd == 'delete':
                        self.catalog, flag = self.UserManager.deleteUser(
                            self.catalog, userID)

                        if flag == 0:
                            contents = json.dumps(self.catalog)
                            return contents
                        elif flag == 1:
                            raise cherrypy.HTTPError(507, "User not found")
                    else:
                        raise cherrypy.HTTPError(
                            401, "Unexpected command - Wrong Command ")
                    if flag == 1:
                        raise cherrypy.HTTPError(507, "User not found")
                    else:
                        contents = json.dumps(self.catalog)
                        return contents


                elif ID_type.upper() == 'R_':
                    # controllare se è un'azione riferita alle camere o a un
                    # device
                    if len(uri) > 3:
                        # controllare a quale azione riguardo i device si
                        # riferisce
                        roomID = IDReference
                        deviceID = uri[2]
                        cmd = uri[3]
                        ID_type2 = deviceID[0:2]
                        if ID_type2.upper() == 'D_':
                            if cmd == 'delete':
                                self.catalog, flag = self.DeviceManager.deleteDevice(
                                    self.catalog, roomID, deviceID)
                            elif cmd == "delete_service_details":
                                serviceType = uri[4]
                                self.catalog, flag = self.DeviceManager.deleteService(
                                    self.catalog, roomID, deviceID, serviceType)
                            else:
                                raise cherrypy.HTTPError(
                                    401, "Unexpected command - Wrong Command ")
                            if flag == 2:
                                raise cherrypy.HTTPError(
                                    505, "Device not found")
                            elif flag == 3:
                                raise cherrypy.HTTPError(
                                    506, "Room not found")
                            else:
                                contents = json.dumps(self.catalog)
                                return contents
                        else:
                            raise cherrypy.HTTPError(
                                400, "Unexpected command - ID NOT CLASSIFIED ")

                    else:
                        # controllare a quale azione riguardo le stanze si
                        # riferisce
                        roomID = IDReference
                        cmd = uri[2]
                        if cmd == 'delete':
                            self.catalog, flag = self.RoomManager.deleteRoom(
                                self.catalog, roomID)
                            if flag == 3:
                                raise cherrypy.HTTPError(506, "Room not found")
                            else:
                                contents = json.dumps(self.catalog)
                                return contents

                        else:
                            raise cherrypy.HTTPError(
                                401, "Unexpected command - Wrong Command ")

                else:
                    raise cherrypy.HTTPError(
                        400, "Unexpected command - ID NOT CLASSIFIED ")


if __name__ == "__main__":
    Settings = json.load(open("Settings.json"))
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on': True
        }
    }
    cherrypy.tree.mount(WareHouse_Catalog(Settings),'/',conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0','server.socket_port': Settings['port_catalog']})
    cherrypy.engine.start()
    cherrypy.engine.block()
