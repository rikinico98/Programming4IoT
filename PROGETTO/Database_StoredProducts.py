# Database of all the stored products

import cherrypy
import json
import requests
from datetime import datetime
import ProductManager as pm

class Database_StoredProducts():
    exposed = True

    def __init__(self):
        dateTimeObj = datetime.now()
        currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second} "
        self.database = {
            "lastUpdate": currentTime,
            "roomList": [],
        }
        self.ProductManager = pm.ProductManager()

#########################################################################################################
# impostare la richiesta REST in modo tale da avere

        # GET
        # db/all
        # db/ID_stanza/all
        # db/ID_stanza/ID_prodotto/all
        # db/quantity/num/all
        # db/ID_stanza/quantity/num/all

        # PUT
        # db/ID_stanza/ID_prodotto/new
        # body atteso:
        # {"product_ID" : ID_prodotto,
        #   "quantity": numero intero,
        #   "product_type": codice_prodotto}

        # DELETE
        # db/ID_stanza/ID_prodotto/delete
        # body atteso:
        # {"product_ID" : ID_prodotto, "quantity": numero intero, "product_type": codice_prodotto}
        # NOTA!!!! : il body passato al DELETE deve essere una sola riga!!!!

#########################################################################################################

    def GET(self, *uri):
        uri = list(uri)
        contents = {
            "products" : []
        }
        if len(uri) == 2:
            if uri[1] != "all":
                raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
            else:
                # db/all
                contents, flag = self.ProductManager.returnAllProducts(self.database["roomList"])
                return json.dumps(contents)
        elif len(uri) > 2:
            if uri[1] == "quantity":
                if uri[3] != "all":
                    raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                else:
                    # db/quantity/num/all
                    quantity = uri[2]
                    contents, flag = self.ProductManager.thresholdAllProducts(self.database["roomList"], quantity)
                    return json.dumps(contents)
            else:
                room_ID = uri[1]
                if uri[2] == "all":
                    # db/ID_stanza/all
                    room, flag = self.ProductManager.searchRoom(self.database["roomList"], room_ID)
                    if flag == 1:
                        raise cherrypy.HTTPError(506, "Room not found")
                    else:
                        contents, flag = self.ProductManager.returnAllRoomProducts(room)
                        return json.dumps(contents)
                elif uri[2] == "quantity":
                    if uri[4] != "all":
                        raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                    else:
                        # db/ID_stanza/quantity/num/all
                        quantity = uri[3]
                        room, flag = self.ProductManager.searchRoom(self.database["roomList"], room_ID)
                        if flag == 1:
                            raise cherrypy.HTTPError(506, "Room not found")
                        else:
                            contents, flag = self.ProductManager.thresholdAllRoomProducts(room, quantity)
                            return json.dumps(contents)
                elif uri[3] != "all":
                    raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                else:
                    # db/ID_stanza/ID_prodotto/all
                    product_ID = uri[2]
                    room, flag = self.ProductManager.searchRoom(self.database["roomList"], room_ID)
                    if flag == 1:
                        raise cherrypy.HTTPError(506, "Room not found")
                    else:
                        contents, flag = self.ProductManager.returnProducts(room, product_ID)
                        if flag == 1:
                            raise cherrypy.HTTPError(506, "Product not found")
                        else:
                            return json.dumps(contents)
        else:
            raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")

    def PUT(self, *uri):
        body = cherrypy.request.body.read()
        jsonBody = json.loads(body)
        quantity = jsonBody["quantity"]
        product_type = jsonBody["product_type"]
        if len(uri) != 4:
            raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
        else:
            room_ID = uri[1]
            product_ID = uri[2]
            cmd = uri[3]
            if cmd != "new":
                raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
            else:
                current_rooms = []
                # Get all the rooms currently used
                r_rooms = requests.get(f'http://127.0.0.1:8070/catalog/rooms')
                if r_rooms.status_code == 200:
                    j_rooms = json.dumps(r_rooms.json(),indent=4)
                    d_rooms = json.loads(j_rooms)
                    current_rooms_list = d_rooms["roomList"] #Note: rooms is a list
                else:
                    raise cherrypy.HTTPError(506, "Room not found")
                for room in current_rooms_list:
                    current_rooms.append(room["roomID"])
                # Check if ID_stanza is present in the warehouse rooms
                flag_room = 1
                for room in current_rooms:
                    if room == room_ID:
                        flag_room = 0
                if flag_room == 1:
                    # Room is not found
                    raise cherrypy.HTTPError(506, "Room not found")
                else:
                    # Room is found
                    # Check if the product type of the room is equal to the one of the product
                    for room in current_rooms_list:
                        if room["roomID"] == room_ID:
                            if room["product_type"] != product_type:
                                raise cherrypy.HTTPError(400, "Product type different from the room one")
                    # Check if there are already products in the room
                    flag_room = 1
                    for room in self.database["roomList"]:
                        if room["room_ID"] == room_ID:
                            flag_room = 0
                            # If there are already products in the room
                            # Check if the product is already present
                            flag_product = 1
                            for product in room["products"]:
                                if product["product_ID"] == product_ID:
                                    flag_product = 0
                                    # If the product is already present
                                    # Update its quantity
                                    product["quantity"] = product["quantity"] + quantity
                            # If the product is new
                            if flag_product == 1:
                                room["products"].append(jsonBody)
                    # If room is empty
                    if flag_room == 1:
                        myDict = {
                            "room_ID": room_ID,
                            "products": []
                        }
                        myDict["products"].append(jsonBody)
                        self.database["roomList"].append(myDict)
        dateTimeObj = datetime.now()
        currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second} "
        self.database["lastUpdate"] = currentTime
        contents = json.dumps(self.database)
        return contents

    def DELETE(self, *uri):
        body = cherrypy.request.body.readline()
        jsonBody = json.loads(body)
        quantity = jsonBody["quantity"]
        product_type = jsonBody["product_type"]
        if len(uri) != 4:
            raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
        else:
            room_ID = uri[1]
            product_ID = uri[2]
            cmd = uri[3]
            if cmd != "delete":
                raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
            else:
                current_rooms = []
                # Get all the rooms currently used
                r_rooms = requests.get(f'http://127.0.0.1:8070/catalog/rooms')
                if r_rooms.status_code == 200:
                    j_rooms = json.dumps(r_rooms.json(),indent=4)
                    d_rooms = json.loads(j_rooms)
                    current_rooms_list = d_rooms["roomList"] #Note: rooms is a list
                else:
                    raise cherrypy.HTTPError(506, "Room not found")
                for room in current_rooms_list:
                    current_rooms.append(room["roomID"])
                # Check if ID_stanza is present in the warehouse rooms
                flag_room = 1
                for room in current_rooms:
                    if room == room_ID:
                        flag_room = 0
                if flag_room == 1:
                    # Room is not found
                    raise cherrypy.HTTPError(506, "Room not found")
                else:
                    # Room is found
                    # Check if the product type of the room is equal to the one of the product
                    for room in current_rooms_list:
                        if room["roomID"] == room_ID:
                            if room["product_type"] != product_type:
                                raise cherrypy.HTTPError(400, "Product type different from the room one")
                    # Check if there are already products in the room
                    flag_room = 1
                    for room in self.database["roomList"]:
                        if room["room_ID"] == room_ID:
                            flag_room = 0
                            # If there are already products in the room
                            # Check if the product is already present
                            flag_product = 1
                            for product in room["products"]:
                                if product["product_ID"] == product_ID:
                                    flag_product = 0
                                    # If the product is already present
                                    # Update its quantity
                                    if quantity <= product["quantity"]:
                                        product["quantity"] = product["quantity"] - quantity
                                    else:
                                        raise cherrypy.HTTPError(413, "There are not enough products to sell")
                            # If the product is new
                            if flag_product == 1:
                                raise cherrypy.HTTPError(413, "There are not enough products to sell")
                    # If room is empty
                    if flag_room == 1:
                        raise cherrypy.HTTPError(413, "There are not enough products to sell")
        dateTimeObj = datetime.now()
        currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second} "
        payload = {
            "product_ID": product_ID,
            "quantity": quantity,
            "month": dateTimeObj.month,
            "year": dateTimeObj.year,
            "product_type": product_type
            
        }
        requests.put(f'http://127.0.0.1:8090/db/{room_ID}/{product_ID}/new', data = json.dumps(payload))
        self.database["lastUpdate"] = currentTime
        contents = json.dumps(self.database)
        return contents

if __name__ == "__main__":
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on': True
        }
    }
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.quickstart(Database_StoredProducts(), '/', conf)