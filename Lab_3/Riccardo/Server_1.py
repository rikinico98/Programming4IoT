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
		cond1 = (len(uri) != 0)
		cond2 =(len(params)>1)
		if cond1 and cond2 :
			if uri[0] =='add':
				operands= list(params.values())
				self.operation.add(float(operands[0]),float(operands[1]))
				output = dict(operation='add',  op1=operands[0],  op2=operands[1],  result=self.operation.result)
				JSON_out= json.dumps(output)
				return JSON_out

			elif uri[0] =='sub':
				operands = list(params.values())
				self.operation.sub(float(operands[0]),float(operands[1]))
				output = dict(operation='sub',  op1=operands[0],  op2=operands[1],  result=self.operation.result)
				JSON_out= json.dumps(output)
				return JSON_out
			elif uri[0] =='mul':
				operands = list(params.values())
				self.operation.mul(float(operands[0]),float(operands[1]))
				output = dict(operation='mul',  op1=operands[0],  op2=operands[1],  result=self.operation.result)
				JSON_out= json.dumps(output)
				return JSON_out
			elif uri[0] =='div':
				operands = list(params.values())
				if(int(operands[1]) !=0):
					self.operation.div(float(operands[0]),float(operands[1]))
					output = dict(operation='div', op1=operands[0], op2=operands[1], result=self.operation.result)
					JSON_out = json.dumps(output)
					return JSON_out
				else:
					raise cherrypy.HTTPError(403, "Zero division")
			else:
				raise cherrypy.HTTPError(404, "Wrong Command")
		else:
			if (not cond1):
				raise cherrypy.HTTPError(405, "Empty Uri")
			elif (not cond2):
				raise cherrypy.HTTPError(406, "Lack of operator")





if __name__=="__main__":



	# Standard configuration to serve the url "localhost:8080"
	conf = {
		'/': {
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tool.session.on': True
		}
	}
	cherrypy.config.update({'server.socket_port': 8080})
	cherrypy.quickstart(CalculatorSimpleREST(), '/', conf)
	cherrypy.engine.start()
	cherrypy.engine.block()



