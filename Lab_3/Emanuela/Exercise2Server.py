##EX2 ESTENSIONE DELL'ESERCIZIO 3 DEL LAB2 
import json
import cherrypy
import os
from classManageDevices import* 
##############################################
class SERVER():
    exposed=True
    def __init__(self):
        ld=ListDevice()
        self.ld=ld
    def GET(self,*uri,**params):
        L='DEVICES'  
        # L+='<br>'

        if len(uri)!=0:
            if uri[0]=='exit':
                L+=self.ld.exit()
            elif uri[0]=='printall':
                L+=self.ld.printall()
            else:
                paramskey=params.keys()
                paramsv=list(params.values())
                paramsvalue=paramsv[0]
                if uri[0]=='name':
                    L+=self.ld.searchByName(paramsvalue)
                elif uri[0]=='id':
                    L+=self.ld.searchbyID(int(paramsvalue))
                elif uri[0]=='service':
                    L+=self.ld.searchbyservice(paramsvalue)
                    
                elif uri[0]=='type':
                    L+=self.ld.searchbyMeasureType(paramsvalue)
            
        return (json.dumps(L))
    def PUT(self):
        
        body=cherrypy.request.body.read()
        jsonBody=json.loads(body)
        print(jsonBody)
        L=self.ld.insert_device(jsonBody)
        return (json.dumps(L))
           
if __name__=="__main__":
#Standard configuration to serve the url "localhost:8080"
    conf={
    '/':{
    'request.dispatch':cherrypy.dispatch.MethodDispatcher(),'tool.session.on':True
    } } 
    cherrypy.quickstart(SERVER(),'/',conf)