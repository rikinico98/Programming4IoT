import json
import cherrypy
import os
import requests

class SERVER():
    exposed=True
    def __init__(self):
        self.url = "https://www.bicing.barcelona/en/get-stations"
        pass

    def GET(self,*uri,**params):
        solution = '' 
        if len(uri)!=0:
            r=requests.get(f'{self.url}/')
            paramsv=list(params.values())
            d=json.loads(r.text)
            if uri[0]=='slots':
                slots = []
                for it in range(len(d["stations"][:])):
                    slots.append(d["stations"][it]["slots"])
                if paramsv[1] == "descending":
                    indexSorted = sorted(range(len(slots)), key=lambda k: slots[k], reverse = True)
                else: #Ascending
                    indexSorted = sorted(range(len(slots)), key=lambda k: slots[k], reverse = False)
                for it in range(int(paramsv[0])):
                    solution += str(d["stations"][indexSorted[it]])
                solution = json.dumps(solution)
            if uri[0] == 'bikes':
                bikes = []
                for it in range(len(d["stations"][:])):
                    bikes.append(d["stations"][it]["bikes"])
                if paramsv[1] == "descending":
                    indexSorted = sorted(range(len(bikes)), key=lambda k: bikes[k], reverse = True)
                else: #Ascending
                    indexSorted = sorted(range(len(bikes)), key=lambda k: bikes[k], reverse = False)
                for it in range(int(paramsv[0])):
                    solution += str(d["stations"][indexSorted[it]])
                solution = json.dumps(solution)
            if uri[0] == 'stations':
                for it in range(len(d["stations"][:])):
                    if int(d["stations"][it]["electrical_bikes"]) >= int(paramsv[0]):
                        if int(d["stations"][it]["slots"]) >= int(paramsv[1]):
                            solution += str(d["stations"][it])
                solution = json.dumps(solution)
            if uri[0] == 'count':
                bikes = 0
                slots = 0
                for it in range(len(d["stations"][:])):
                    bikes += int(d["stations"][it]["bikes"])
                    slots += int(d["stations"][it]["slots"])
                solution = {
                    "bikes" : bikes,
                    "slots" : slots
                }
                return json.dumps(solution)
        return json.loads(solution)
           
if __name__=="__main__":
    conf={
            '/':{
                    'request.dispatch':cherrypy.dispatch.MethodDispatcher(),'tool.session.on':True
                } 
    } 
    cherrypy.quickstart(SERVER(),'/',conf)