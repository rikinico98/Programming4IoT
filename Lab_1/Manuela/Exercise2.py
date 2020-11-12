# Develope a simple calculator
from classCalculator import Calculator
import json

if __name__=="__main__":
    op = None
    jsonFile = open("ResultEx2.json","a")
    jsonFile.write("{\n")
    index = 0
    while op != "exit":
        num = []
        solution = None
        end = True
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
            print("Input the values, end for ending")
            while end == True:
                temp = input()
                if temp == "end":
                    end = False
                else:
                    num.append(int(temp))
            result = Calculator(num[0],num[1],op)
            solution = result.Solve()
            for it in range(len(num)-2):
                result = Calculator(solution, num[it+2], op)
                solution = result.Solve()
            myDict = {
                "Operands": num,
                "Operation": op,
                "Result": solution
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