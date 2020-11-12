from Exercise2Server import *
from diz import *
import cherrypy
import json
import requests

if __name__ == "__main__":
    
    while True: 
        operation=input(" inserire l'operazione da eseguire exit,name,id,type,service,printall, insert_device or Q to end calculations: ")
        if operation != 'Q':
            if operation != 'printall' and operation !='exit' and operation != 'insert':
                operand1=(input('inserire il parametro:'))
                r=requests.get(f'http://127.0.0.1:8080/{operation}?op1={operand1}')
                j=json.dumps(r.json(),indent=4)
                d=json.loads(j) 
                print(d)
                
            elif operation =='exit' or operation=='printall':
                r=requests.get(f'http://127.0.0.1:8080/{operation}')
                j=json.dumps(r.json(),indent=4)
                d=json.loads(j) 
                if operation=='exit':
                    print('------>changes saved End of Program!')
                    break
                else :
                    print(d) 
           
            elif operation=='insert':
                newdev=NEWDEVICE()
                payload=newdev.insert_new_device()
                response=requests.put('http://127.0.0.1:8080',data=payload)
                json_response=response.json()
                print(response.request.body)
                print('type exit too save changes and stop the program')

