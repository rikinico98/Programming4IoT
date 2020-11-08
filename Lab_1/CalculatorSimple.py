import json
class CalculatorSimple():
	"""Contact defined by his name surname and emal"""
	def __init__(self,filename):
		self.fileName=filename
		self.l_o=0
		self.r_o = 0
		self.result=0
		self.jsonContent=[]
		open(self.fileName, 'w').close()

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



	def save(self,operation):
		tmp_dic={}
		opContent = dict(operation=operation, left_operand= self.l_o, right_operand = self.r_o, result=self.result)
		self.jsonContent.append(opContent)

	def save_all(self):
		all={}
		all['all_operation']=self.jsonContent
		json.dump(all, open(self.fileName, 'a', ), indent=4)


