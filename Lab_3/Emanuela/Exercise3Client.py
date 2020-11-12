from Exercise3Server import *
import cherrypy
import json
import requests

if __name__ == "__main__":
    
    while True: 
        operation=input(" inserire l'operazione da eseguire\n\
             [slots] for order the bike-stations by available “slots” and display first N stations\n\
             [bikes] for order the bike-stations by available “bikes” and display first N stations\n\
             [stations] for get all the bike-stations with more than N available “electrical_bikes” and more than M free “slots”\n\
             [count] for count all the available “bikes” and all the free “slots” in the city\n\
             [Q] to end calculations\n: ")
        if operation != "Q":
            if operation == "slots" or operation == "bikes":
                choice = input("\nNumber of stations to display. It is optional and by default N=10 ---> Y/N? ")
                if choice == "Y":
                    N = int(input("N = "))
                else:
                    N = 10
                choice = input("\nOrdering. Default value is descending ---> Y/N? ")
                if choice == "Y":
                    ordering = input("Order = ")
                else:
                    ordering = "descending"
                r=requests.get(f'http://127.0.0.1:8080/{operation}?N={N}&Order={ordering}')
                print(r.text)
            if operation == "stations":
                choice = input("\nNumber of stations to display. It is optional and by default N=10 ---> Y/N? ")
                if choice == "Y":
                    N = int(input("N = "))
                else:
                    N = 10
                choice = input("\nNumber of free slots. It is optional and by default M=5 ---> Y/N? ")
                if choice == "Y":
                    M = input("M = ")
                else:
                    M = 5
                r=requests.get(f'http://127.0.0.1:8080/{operation}?N={N}&Order={M}')
                print(r.text)
            if operation == "count":
                r=requests.get(f'http://127.0.0.1:8080/{operation}')
                print(r.text)
        else:
            break