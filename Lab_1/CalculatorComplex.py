import json
class CalculatorComplex():
	"""Contact defined by his name surname and emal"""
	def __init__(self,filename):
		self.fileName=filename
		self.operands= []
		self.result=0
		self.jsonContent=[]
		open(self.fileName, 'w').close()

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
				return 0
			self.result = self.result / operand
		else:
			print("You are dividing by zero, dumb!")
			return 1

	def clear(self):
		self.operands=[]
		self.result=0

	def save(self,operation):
		opContent = dict(operation=operation, operands = self.operands, result=self.result)
		self.jsonContent.append(opContent)

	def save_all(self):
		all = {}
		all['all_operation'] = self.jsonContent
		json.dump(all, open(self.fileName, 'a', ), indent=4)


