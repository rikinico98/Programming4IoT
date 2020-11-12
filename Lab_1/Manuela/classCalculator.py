class Calculator():

    def __init__(self, numberOne,numberTwo,operation):
        self.numberOne = numberOne
        self.numberTwo = numberTwo
        self.operation = operation
        self.result = None
        
    def Solve(self):
        if self.operation == "add":
            self.result = self.numberOne + self.numberTwo
        elif self.operation == "sub":
            self.result = self.numberOne - self.numberTwo
        elif self.operation == "mul":
            self.result = self.numberOne * self.numberTwo
        elif self.operation == "div":
            try:
                self.result = self.numberOne / self.numberTwo
            except ZeroDivisionError:
                print("The second number can not be zero")
        return self.result