import CalculatorComplex as mycalc

if __name__=="__main__":

	calc= mycalc.CalculatorComplex('ciao.json')
	print('Welcome to the application CALCULATOR')
	c=''
	helpMessage="Insert 'add' to perform add operation \nPress 'sub' to perform subtraction\nPress 'mul' to perform multiplication\nPress 'div' to perform division\nPress 'e' to exit the program\nFollowed by operands divided by space"
	while True:
		print(helpMessage)
		command=input()
		command=' '.join(command.split())
		command=command.split(' ')
		cmd=command[0]
		operands = command[1:]
		if cmd=='add':
			for op in operands:
				if op.lstrip('-').isdigit():
					calc.add(float(op))
					error=0
				else:
					error=1
			if error:
					print("Bro you don't type a number")
			else:
					calc.save(cmd)
					calc.clear()


		elif cmd=='sub':
			i=0
			for op in operands:
				if op.lstrip('-').isdigit():
					calc.sub(float(op),i)
					error = 0
				else:
					error = 1
				i+=1
			if error:
				print("Bro you don't type a number")
			else:
				calc.save(cmd)
				calc.clear()



		elif cmd=='mul':
			i=0
			for op in operands:
				if op.lstrip('-').isdigit():
					calc.mul(float(op),i)
					error=0
				else:
					error=1
				i+=1
			if error:
					print("Bro you don't type a number")
			else:
					calc.save(cmd)
					calc.clear()



		elif cmd=='div':

			for op in operands:
				i = 0
				if op.lstrip('-').isdigit():

					error = calc.div(float(op), i)
					if (not error):
						i += 1
					else:
						calc.clear()
						break
				else:
					calc.clear()
					print("Bro you don't type a number")
					break




		elif cmd=='e':

			break
		else:
			print('Command not available')


	calc.save_all()
