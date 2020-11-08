import json
import cherrypy

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
		self.operation=CalculatorSimple()

	def GET(self, *uri,**params):

		if len(uri) != 0:
			if uri[0] =='add':
				operands= list(uri)
				self.operation.add(float(operands[1]),float(operands[2]))
				output = dict(operation='add',  op1=operands[1],  op2=operands[2],  result=self.operation.result)
				JSON_out= json.dumps(output)
				return JSON_out

			elif uri[0] =='sub':
				operands = list(uri)
				self.operation.sub(float(operands[1]),float(operands[2]))
				output = dict(operation='sub',  op1=operands[1],  op2=operands[2],  result=self.operation.result)
				JSON_out= json.dumps(output)
				return JSON_out
			elif uri[0] =='mul':
				operands = list(uri)
				self.operation.mul(float(operands[1]),float(operands[2]))
				output = dict(operation='mul',  op1=operands[1],  op2=operands[2],  result=self.operation.result)
				JSON_out= json.dumps(output)
				return JSON_out
			elif uri[0] =='div':
				operands = list(uri)
				if(int(operands[2]) !=0):
					self.operation.div(float(operands[1]),float(operands[2]))
					output = dict(operation='div', op1=operands[1], op2=operands[2], result=self.operation.result)
					JSON_out = json.dumps(output)
					return JSON_out
				else:
					JSON_Out = 'Division by 0'


			else:
				JSON_Out='MAN YOU TYPE WRONG COMMAND'



		return JSON_Out


if __name__=="__main__":



	# Standard configuration to serve the url "localhost:8080"
	conf = {
		'/': {
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tool.session.on': True
		}
	}
	cherrypy.config.update({'server.socket_port': 8090})
	cherrypy.quickstart(CalculatorSimpleREST(), '/', conf)


	calc.save_all()
