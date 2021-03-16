# Database of sold products

import cherrypy
import json
import requests
from datetime import datetime
import ProductManager as pm

class Database_SoldProducts():
    exposed = True

    def __init__(self):
        dateTimeObj = datetime.now()
        currentTime = f"{dateTimeObj.day}/{dateTimeObj.month}/{dateTimeObj.year}, {dateTimeObj.hour}:{dateTimeObj.minute}:{dateTimeObj.second} "
        self.database = {
            "lastUpdate": currentTime,
            "roomList": [],
        }
        self.ProductManager = pm.ProductManager()

###########################################################
# impostare la richiesta REST in modo tale da avere

        # GET
        # db/all
        # db/most/all
        # db/least/all
        # db/ID_stanza/most/all
        # db/ID_stanza/least/all
        # db/most/month/all
        # db/least/month/all
        # db/ID_stanza/most/month/all
        # db/ID_stanza/least/month/all
        # db/most/year/all
        # db/least/year/all
        # db/ID_stanza/most/year/all
        # db/ID_stanza/least/year/all

        # PUT
        # db/ID_stanza/ID_prodotto/new
        # body atteso:
        # {"product_ID" : ID_prodotto,
        #   "quantity": numero intero,
        #   "month" : mese,
        #   "year" : year,
        #   "product_type": codice_prodotto}

###########################################################

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
            if uri[1] == "most":
                if uri[2] != "all":
                    if uri[3] != "all":
                        raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                    else:
                        date = int(uri[2])
                        if date > 0 and date < 13:
                            # db/most/month/all
                            contents, flag = self.ProductManager.mostSoldMonthProduct(self.database["roomList"], date)
                            if flag == 1:
                                raise cherrypy.HTTPError(506, "Month not found")
                            else:
                                return json.dumps(contents)
                        elif date > 2000:
                            # db/most/year/all
                            contents, flag = self.ProductManager.mostSoldYearProduct(self.database["roomList"], date)
                            if flag == 1:
                                raise cherrypy.HTTPError(506, "Year not found")
                            else:
                                return json.dumps(contents)
                        else:
                             raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                else:
                    # db/most/all
                    contents, flag = self.ProductManager.mostSoldProduct(self.database["roomList"])
                    return json.dumps(contents)
            elif uri[1] == "least":
                if uri[2] != "all":
                    if uri[3] != "all":
                        raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                    else:
                        date = int(uri[2])
                        if date > 0 and date < 13:
                            # db/least/month/all
                            contents, flag = self.ProductManager.leastSoldMonthProduct(self.database["roomList"], date)
                            if flag == 1:
                                raise cherrypy.HTTPError(506, "Month not found")
                            else:
                                return json.dumps(contents)
                        elif date > 2000:
                            # db/least/year/all
                            contents, flag = self.ProductManager.leastSoldYearProduct(self.database["roomList"], date)
                            if flag == 1:
                                raise cherrypy.HTTPError(506, "Year not found")
                            else:
                                return json.dumps(contents)
                        else:
                             raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                else:
                    # db/least/all
                    contents, flag = self.ProductManager.leastSoldProduct(self.database["roomList"])
                    return json.dumps(contents)
            else:
                room_ID = uri[1]
                if uri[2] =="most":
                    if uri[3] == "all":
                        # db/ID_stanza/most/all
                        room, flag = self.ProductManager.searchRoom(self.database["roomList"], room_ID)
                        if flag == 1:
                            raise cherrypy.HTTPError(506, "Room not found")
                        else:
                            quantity_max = self.ProductManager.findMaximum(room)
                            contents, flag = self.ProductManager.quantityProduct(room, quantity_max)
                            if flag == 1:
                                raise cherrypy.HTTPError(506, "Product not found")
                            else:
                                return json.dumps(contents)
                    else:
                        date = int(uri[3])
                        if date > 0 and date < 13:
                            # db/ID_stanza/most/month/all
                            room, flag = self.ProductManager.searchRoom(self.database["roomList"], room_ID)
                            if flag == 1:
                                raise cherrypy.HTTPError(506, "Room not found")
                            else:
                                contents, flag = self.ProductManager.mostSoldMonthProduct([room], date)
                                if flag == 1:
                                    raise cherrypy.HTTPError(506, "Month not found")
                                else:
                                    return json.dumps(contents)
                        elif date > 2000:
                            # db/ID_stanza/most/year/all
                            room, flag = self.ProductManager.searchRoom(self.database["roomList"], room_ID)
                            if flag == 1:
                                raise cherrypy.HTTPError(506, "Room not found")
                            else:
                                contents, flag = self.ProductManager.mostSoldYearProduct([room], date)
                                if flag == 1:
                                    raise cherrypy.HTTPError(506, "Year not found")
                                else:
                                    return json.dumps(contents)
                        else:
                            raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                elif uri[2] == "least":
                    if uri[3] == "all":
                        # db/ID_stanza/least/all
                        room, flag = self.ProductManager.searchRoom(self.database["roomList"], room_ID)
                        if flag == 1:
                            raise cherrypy.HTTPError(506, "Room not found")
                        else:
                            quantity_min = self.ProductManager.findMinimum(room)
                            contents, flag = self.ProductManager.quantityProduct(room, quantity_min)
                            return json.dumps(contents)
                    else:
                        date = int(uri[3])
                        if date > 0 and date < 13:
                            # db/ID_stanza/least/month/all
                            room, flag = self.ProductManager.searchRoom(self.database["roomList"], room_ID)
                            if flag == 1:
                                raise cherrypy.HTTPError(506, "Room not found")
                            else:
                                contents, flag = self.ProductManager.leastSoldMonthProduct([room], date)
                                if flag == 1:
                                    raise cherrypy.HTTPError(506, "Month not found")
                                else:
                                    return json.dumps(contents)
                        elif date > 2000:
                            # db/ID_stanza/least/year/all
                            room, flag = self.ProductManager.searchRoom(self.database["roomList"], room_ID)
                            if flag == 1:
                                raise cherrypy.HTTPError(506, "Room not found")
                            else:
                                contents, flag = self.ProductManager.leastSoldYearProduct([room], date)
                                if flag == 1:
                                    raise cherrypy.HTTPError(506, "Year not found")
                                else:
                                    return json.dumps(contents)
                        else:
                            raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
                else:
                    raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")
        else:
            raise cherrypy.HTTPError(401, "Unexpected command - Wrong Command")

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