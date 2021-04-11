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

    # Search roomID in roomList
    # return the correct room and the flag = 0 if present
    # else return an empty list and the flag = 1
    def searchRoom(self, roomList, roomID):
        roomFound = 1
        for room in roomList:
            if room['room_ID'] == roomID:
                roomFound = 0
                return room, roomFound
        room = []
        return room, roomFound

    # Return a list that contains all the products and 
    # the flag = 0 if some product is present
    # else return an empty list and the flag = 1
    def returnAllProducts(self, roomList):
        productsFound = 1
        products = []
        for room in roomList:
            productList, flag = self.returnAllRoomProducts(room)
            products = products + productList
        if len(products) != 0:
            productsFound = 0
        return products, productsFound

    # Return a list that contains all the products within a room
    # and the flag = 0 if some product is present in that room
    # else return an empty list and the flag = 1
    def returnAllRoomProducts(self, room):
        productsFound = 1
        products = []
        for product in room["products"]:
            productsFound = 0
            products.append(product)
        return products, productsFound

    # Return a list that contains all the products 
    # whose quantity is smaller than a givent threshold and 
    # the flag = 0 if some product is present
    # else return an empty list and the flag = 1
    def thresholdAllProducts(self, roomList, quantity):
        productsFound = 1
        products = []
        for room in roomList:
            productList, flag = self.thresholdAllRoomProducts(room, quantity)
            products = products + productList
        if len(products) != 0:
            productsFound = 0
        return products, productsFound

    # Return a list that contains all the products within a room
    # whose quantity is smaller than a givent threshold and 
    # the flag = 0 if some product is present in that room
    # else return an empty list and the flag = 1
    def thresholdAllRoomProducts(self, room, quantity):
        productsFound = 1
        products = []
        for product in room["products"]:
            if product["quantity"] <= int(quantity):
                productsFound = 0
                products.append(product)
        return products, productsFound

    # Search productID in all the products within a room
    # return the correct products as a list and the flag = 0 if present
    # else return an empty list and the flag = 1
    def returnProducts(self, room, productID):
        productsFound = 1
        products = []
        for product in room["products"]:
            if product["product_ID"] == productID:
                productsFound = 0
                products.append(product)
        return products, productsFound

    # Return the minimum quantity of the products within a room
    def findMinimum(self, room):
        quantity_min = sys.maxsize
        for product in room["products"]:
            if product["quantity"] < quantity_min:
                quantity_min = product["quantity"]
        return quantity_min

    # Return the maximum quantity of the products within a room
    def findMaximum(self, room):
        quantity_max = 0
        for product in room["products"]:
            if product["quantity"] > quantity_max:
                quantity_max = product["quantity"]
        return quantity_max

    # Return the overall most sold products and the flag = 0
    # If no products are present return an empty list and the flag = 1
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

    # Return the overall least sold products and the flag = 0
    # If no products are present return an empty list and the flag = 1
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

    # Return all the products within a room whose quantity
    # is equal to some quantity passed as parameter 
    # and the flag = 0 if some is present
    # else it return an empty list and the flag = 1 
    def quantityProduct(self, room, quantity):
        productsFound = 1
        products = []
        for product in room["products"]:
            if product["quantity"] == quantity:
                productsFound = 0
                products.append(product)
        return products, productsFound

    # Return the most sold products in a given month and the flag = 0
    # If no products are present return an empty list and the flag = 1
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
 
    # Return the most sold products in a given year and the flag = 0
    # If no products are present return an empty list and the flag = 1
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

    # Return the least sold products in a given month and the flag = 0
    # If no products are present return an empty list and the flag = 1
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

    # Return the least sold products in a given year and the flag = 0
    # If no products are present return an empty list and the flag = 1
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