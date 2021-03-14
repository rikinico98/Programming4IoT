# Database of sold products

import cherrypy
import json
import requests
from datetime import datetime

class Database_SoldProducts():
    exposed = True

    def __init__(self):
        dateTimeObj = datetime.now()
        currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second} "
        self.database = {
            "lastUpdate": currentTime,
            "roomList": [],
        }

###########################################################
# impostare la richiesta REST in modo tale da avere

        # PUT
        # db/ID_stanza/ID_prodotto/new
        # body atteso:
        # {"product_ID" : ID_prodotto,
        #   "quantity": numero intero,
        #   "month" : mese,
        #   "year" : year,
        #   "product_type": codice_prodotto}

###########################################################

    def PUT(self, *uri):
        body = cherrypy.request.body.read()
        jsonBody = json.loads(body)
        quantity = jsonBody["quantity"]
        product_type = jsonBody["product_type"]
        month = jsonBody["month"]
        year = jsonBody["year"]
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
                                raise cherrypy.HTTPError(405, "Product type different from the room one")
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
                                    # If the product is already present
                                    if product["year"] == year:
                                        if product["month"] == month:
                                            # Update its quantity
                                            product["quantity"] = product["quantity"] + quantity
                                            flag_product = 0
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

if __name__ == "__main__":
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on': True
        }
    }
    cherrypy.config.update({'server.socket_port': 8090})
    cherrypy.quickstart(Database_SoldProducts(), '/', conf)