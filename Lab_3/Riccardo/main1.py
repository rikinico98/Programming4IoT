import json
import cherrypy
import requests

class CalculatorSimple():
	"""Contact defined by his name surname and emal"""
	def __init__(self):
		self.l_o=0
		self.r_o = 0
		self.result=0
		self.jsonContent=[]


	def add(self,l_o,r_o):
		self.l_o=l_o
		self.r_o=r_o
		self.result=l_o+r_o

	def sub(self,l_o,r_o):
		self.l_o = l_o
		self.r_o = r_o
		self.result=l_o-r_o

	def mul(self,l_o,r_o):
		self.l_o = l_o
		self.r_o = r_o
		self.result=l_o*r_o


	def div(self,l_o,r_o):
		self.l_o = l_o
		self.r_o = r_o
		self.result = l_o / r_o


class CalculatorSimpleREST(CalculatorSimple):
    exposed = True
    def __init__(self):
        self.operation = CalculatorSimple()

    def GET(self, *uri, **params):
        r = requests.get('http://localhost:4040/api/tunnels/main4/')
        publicUrl=r.json()["public_url"]
        cmd=uri[0]
        if len(uri)!=0:
            if cmd== 'add':
                operands = list(params.values())
                self.operation.add(float(operands[0]), float(operands[1]))
                output = dict(operation='add', op1=operands[0], op2=operands[1], result=self.operation.result)
                JSON_out = json.dumps(output)
                print(JSON_out)

            elif cmd == 'sub':
                operands = list(params.values())
                self.operation.sub(float(operands[0]), float(operands[1]))
                output = dict(operation='sub', op1=operands[0], op2=operands[1], result=self.operation.result)
                JSON_out = json.dumps(output)
                print(JSON_out)
                return JSON_out
            elif cmd == 'mul':
                operands = list(params.values())
                self.operation.mul(float(operands[0]), float(operands[1]))
                output = dict(operation='mul', op1=operands[0], op2=operands[1], result=self.operation.result)
                JSON_out = json.dumps(output)
                print(JSON_out)
                return JSON_out
            elif cmd == 'div':
                operands = list(params.values())
                if (int(operands[1]) != 0):
                    self.operation.div(float(operands[0]), float(operands[1]))
                    output = dict(operation='div', op1=operands[0], op2=operands[1], result=self.operation.result)
                    JSON_out = json.dumps(output)
                    print(JSON_out)
                    return JSON_out
                else:
                    JSON_out = 'Division by 0'
                    print(JSON_out)
            else:
                JSON_out = 'MAN YOU TYPE WRONG COMMAND'
                print(JSON_out)





if __name__ == "__main__":

    #
    # command = input('Inserisci i dati:  \n')
    # command = ' '.join(command.split())
    # command = command.split(' ')
    # cmd = command[0]
    # operands = command[1:]
    # PARAMS = {'op1':operands[0],'op2':operands[1]}
    # URL=publicUrl+'/'+cmd
    # Standard configuration to serve the url "localhost:8080"
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on': True
        }
    }
    cherrypy.config.update({'server.socket_port': 8089})
    cherrypy.quickstart(CalculatorSimpleREST(), '/', conf)
    cherrypy.engine.start()
    s = requests.get(url = URL, params = PARAMS)
    cherrypy.engine.block()





























