import cherrypy
import json
from classCalculator import Calculator

class SimpleCalculator ():
    exposed=True

    def __init__(self):
        pass

    def GET (self,*uri):
        if len(uri) != 3:
            raise cherrypy.HTTPError(400,"Wrong number of parameter")
        valuesList = [int(uri[1]), int(uri[2])]
        if str(uri[0]) != "add" and str(uri[0]) != "sub" and str(uri[0]) != "mul" and str(uri[0]) != "div":
            raise cherrypy.HTTPError(400,"Operation not found")
        ObjectCalc = Calculator(valuesList[0],valuesList[1], str(uri[0]))
        myDict = {
                "FirstOperand": int(uri[1]),
                "SecondOperand": int(uri[2]),
                "Operation": str(uri[0]),
                "Result": ObjectCalc.Solve()
            }
        if myDict["Result"] == None:
            raise cherrypy.HTTPError(403,"Division by zero not allowed")
        Output = json.dumps(myDict,indent=4)
        return Output

if __name__=="__main__":
    #Standard configuration to serve the url "localhost:8080"
    conf={
        '/':{
            'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on':True
        }
    }
    cherrypy.config.update({'server.socket_port': 8090}) #Change the port of the HTTP file created
    cherrypy.quickstart(SimpleCalculator(),'/',conf)