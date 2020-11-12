import json
import cherrypy
class CalculatorComplex():

	def __init__(self):
		self.operands= []
		self.result=0
		self.jsonContent=[]


	def add(self,operand):
		self.operands.append(operand)
		self.result=self.result+operand

	def sub(self,operand,i):
		self.operands.append(operand)
		if (i == 0):
			self.result += operand
			return
		self.result=self.result-operand

	def mul(self,operand,i):
		self.operands.append(operand)
		if (i == 0):
			self.result += operand
			return
		self.result=self.result*operand


	def div(self,operand,i):
		self.operands.append(operand)
		if(operand != 0):
			if(i==0):
				self.result+=operand
			self.result = self.result / operand
		else:
			self.jsonContent="You are dividing by zero, dumb!"


	def clear(self):
		self.operands=[]
		self.result=0

	def save(self,operation):
		opContent = dict(command=operation, operands = self.operands, result=self.result)
		self.jsonContent= json.dumps(opContent)


class CalculatorComplexREST(CalculatorComplex):
    exposed=True
    def __init__(self):
        self.operation=CalculatorComplex()
    def PUT (self):
        body = cherrypy.request.body.read()
        jsonBody = json.loads(body)
        cmd=jsonBody['command']
        operands=jsonBody['operands']
        if "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM" in operands:
            self.operation.jsonContent='One or more element of operands are string'
            return self.jsonContent

        if cmd == 'add':
            for op in operands:
                self.operation.add(float(op))
            self.operation.save(cmd)
            return self.operation.jsonContent

        elif cmd == 'sub':
            i = 0
            for op in operands:
                self.operation.sub(float(op), i)
                i += 1
            self.operation.save(cmd)
            return self.operation.jsonContent


        elif cmd == 'mul':
            i = 0
            for op in operands:
                self.operation.mul(float(op), i)
                i += 1
            self.operation.save(cmd)
            return self.operation.jsonContent

        elif cmd == 'div':
            i = 0
            for op in operands:
                error = self.operation.div(float(op), i)
                if (not error):
                    i += 1
            self.operation.save(cmd)
            return self.operation.jsonContent
		else:
			raise cherrypy.HTTPError(404, "Error message")








if __name__=="__main__":



	# Standard configuration to serve the url "localhost:8080"
	conf = {
		'/': {
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tool.session.on': True
		}
	}
	cherrypy.config.update({'server.socket_port': 8080})
	cherrypy.quickstart(CalculatorComplexREST(), '/', conf)


	calc.save_all()

