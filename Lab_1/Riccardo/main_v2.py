import CalculatorSimple as mycalc

if __name__=="__main__":

	calc= mycalc.CalculatorSimple('ciao.json')
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
			if operands[0].lstrip('-').isdigit() and operands[1].lstrip('-').isdigit():
				calc.add(float(operands[0]),float(operands[1]))
			else:
				print("Bro you don't type a number")
				break

			calc.save(cmd)

		elif cmd=='sub':
			if operands[0].lstrip('-').isdigit() and operands[1].lstrip('-').isdigit():
				calc.sub(float(operands[0]), float(operands[1]))
			else:
				print("Bro you don't type a number")
				break

			calc.save(cmd)
		elif cmd=='mul':
			if operands[0].lstrip('-').isdigit() and operands[1].lstrip('-').isdigit():
				calc.mul(float(operands[0]), float(operands[1]))
			else:
				print("Bro you don't type a number")
				break

			calc.save(cmd)



		elif cmd=='div':
			if(float(operands[1]) != 0):
				if operands[0].lstrip('-').isdigit() and operands[1].lstrip('-').isdigit():
					calc.div(float(operands[0]), float(operands[1]))
				else:
					print("Bro you don't type a number")
					break

				calc.save(cmd)
			else:
				print('You are dividing by 0, man')


		elif cmd=='e':

			break
		else:
			print('Command not available')


	calc.save_all()
