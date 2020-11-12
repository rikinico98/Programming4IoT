import cherrypy
import json
from classCalculator import Calculator

class SimpleCalculator ():
    exposed=True

    def __init__(self):
        pass

    def PUT (self):
        body = cherrypy.request.body.read()
        jsonBody = json.loads(body)
        try:
            operation = jsonBody["command"]
        except:
            raise cherrypy.HTTPError(400,"No command is present")
        if operation != "add" and operation != "sub" and operation != "mul" and operation != "div" and operation != "exit":
            raise cherrypy.HTTPError(400,"Operation not found")
        try:
            operands = jsonBody["operands"]
        except:
            raise cherrypy.HTTPError(400,"No operands are present")
        result = Calculator(int(operands[0]),int(operands[1]),operation)
        solution = result.Solve()
        for it in range(len(operands)-2):
            result = Calculator(solution, int(operands[it+2]), operation)
            solution = result.Solve()
            if solution == None:
                raise cherrypy.HTTPError(403,"Division by zero not allowed")
        myDict = {
                "Operands": operands,
                "Operation": operation,
                "Result": solution
            }
        return json.dumps(myDict,indent=4)

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