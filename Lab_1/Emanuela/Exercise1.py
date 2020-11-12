# Develope a simple calculator with two operator
from classCalculator import Calculator
import json
import requests

if __name__=="__main__":
    op = None
    jsonFile = open("ResultEx1.json","a")
    jsonFile.write("{\n")
    index = 0
    while op != "exit":
        op = input("Insert one of the following key:\n\
                    [1] add: to add the operands and print the JSON\n\
                    [2] sub: to subtact the operands and print the JSON\n\
                    [3] mul: to multiply the operands and print the JSON\n\
                    [4] div: to divide the operands and print the JSON\n\
                    [5] exit: to close the program\n")
        if op != "add" and op != "sub" and op != "mul" and op != "div" and op != "exit":
            print("Invalid operation")
        elif op == "exit":
            break
        else:
            numOne = int(input("Insert the first operand "))
            numTwo = int(input("Insert the second operand "))

            result = Calculator(numOne,numTwo,op)
            myDict = {
                "FirstOperand": numOne,
                "SecondOperand": numTwo,
                "Operation": op,
                "Result": result.Solve()
            }
            if index == 0:
                string = "\"" + str(index) + "\":"
            else:
                string = ",\n\"" + str(index) + "\":"
            jsonFile.write(string)
            jsonFile.write(json.dumps(myDict,indent=4))
            index = index + 1
    jsonFile.write("\n}")
    jsonFile.close()