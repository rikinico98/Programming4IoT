# Helps in managing the products
import sys
from copy import deepcopy

class ProductManager():

    def __init__(self):
        pass

    ##########################################
    # Note:
    # flag = 0 => all is OK!
    # flag = 1 => empty list
    ##########################################

    def searchRoom(self, roomList, roomID):
        roomFound = 1
        for room in roomList:
            if room['room_ID'] == roomID:
                roomFound = 0
                return room, roomFound
        room = []
        return room, roomFound

    def returnAllProducts(self, roomList):
        productsFound = 1
        products = []
        for room in roomList:
            productList, flag = self.returnAllRoomProducts(room)
            products = products + productList
        if len(products) != 0:
            productsFound = 0
        return products, productsFound

    def returnAllRoomProducts(self, room):
        productsFound = 1
        products = []
        for product in room["products"]:
            productsFound = 0
            products.append(product)
        return products, productsFound

    def thresholdAllProducts(self, roomList, quantity):
        productsFound = 1
        products = []
        for room in roomList:
            productList, flag = self.thresholdAllRoomProducts(room, quantity)
            products = products + productList
        if len(products) != 0:
            productsFound = 0
        return products, productsFound

    def thresholdAllRoomProducts(self, room, quantity):
        productsFound = 1
        products = []
        for product in room["products"]:
            if product["quantity"] <= int(quantity):
                productsFound = 0
                products.append(product)
        return products, productsFound

    def returnProducts(self, room, productID):
        productsFound = 1
        products = []
        for product in room["products"]:
            if product["product_ID"] == productID:
                productsFound = 0
                products.append(product)
        return products, productsFound

    def findMinimum(self, room):
        quantity_min = sys.maxsize
        for product in room["products"]:
            if product["quantity"] < quantity_min:
                quantity_min = product["quantity"]
        return quantity_min

    def findMaximum(self, room):
        quantity_max = 0
        for product in room["products"]:
            if product["quantity"] > quantity_max:
                quantity_max = product["quantity"]
        return quantity_max

    def mostSoldProduct(self, roomList):
        productsFound = 1
        products = []
        quantity_max = 0
        for room in roomList:
            quantity_max_room = self.findMaximum(room)
            if quantity_max_room > quantity_max:
                quantity_max = quantity_max_room
        for room in roomList:
            productList = []
            productList, flag = self.quantityProduct(room, quantity_max)
            products = products + productList
        if len(products) != 0:
            productsFound = 0
        return products, productsFound

    def leastSoldProduct(self, roomList):
        productsFound = 1
        products = []
        quantity_min = sys.maxsize
        for room in roomList:
            quantity_min_room = self.findMinimum(room)
            if quantity_min_room < quantity_min:
                quantity_min = quantity_min_room
        for room in roomList:
            productList = []
            productList, flag = self.quantityProduct(room, quantity_min)
            products = products + productList
        if len(products) != 0:
            productsFound = 0
        return products, productsFound

    def quantityProduct(self, room, quantity):
        productsFound = 1
        products = []
        for product in room["products"]:
            if product["quantity"] == quantity:
                productsFound = 0
                products.append(product)
        return products, productsFound

    def mostSoldMonthProduct(self, roomList, month):
        device_to_delete = []
        room_list = deepcopy(roomList)
        for room in roomList:
            for product in room["products"]:
                if month != product["month"]:
                    device_to_delete.append(product)
        for del_device in device_to_delete:
            for i, room in enumerate(roomList):
                for product in room["products"]:
                    if product == del_device:
                        room_list[i]["products"].remove(product)
        products, productsFound = self.mostSoldProduct(room_list)
        return products, productsFound
 
    def mostSoldYearProduct(self, roomList, year):
        device_to_delete = []
        room_list = deepcopy(roomList)
        for room in roomList:
            for product in room["products"]:
                if year != product["year"]:
                    device_to_delete.append(product)
        for del_device in device_to_delete:
            for i, room in enumerate(roomList):
                for product in room["products"]:
                    if product == del_device:
                        room_list[i]["products"].remove(product)
        products, productsFound = self.mostSoldProduct(room_list)
        return products, productsFound

    def leastSoldMonthProduct(self, roomList, month):
        device_to_delete = []
        room_list = deepcopy(roomList)
        for room in roomList:
            for product in room["products"]:
                if month != product["month"]:
                    device_to_delete.append(product)
        for del_device in device_to_delete:
            for i, room in enumerate(roomList):
                for product in room["products"]:
                    if product == del_device:
                        room_list[i]["products"].remove(product)
        products, productsFound = self.leastSoldProduct(room_list)
        return products, productsFound

    def leastSoldYearProduct(self, roomList, year):
        device_to_delete = []
        room_list = deepcopy(roomList)
        for room in roomList:
            for product in room["products"]:
                if year != product["year"]:
                    device_to_delete.append(product)
        for del_device in device_to_delete:
            for i, room in enumerate(roomList):
                for product in room["products"]:
                    if product == del_device:
                        room_list[i]["products"].remove(product)
        products, productsFound = self.leastSoldProduct(room_list)
        return products, productsFound