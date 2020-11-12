import json
import requests

if __name__ == "__main__":
    while True:
        command = input('Inserisci l\'operazione da svolgere :  \n')
        command = ' '.join(command.split())
        command = command.split(' ')
        cmd = command[0]
        if (cmd.upper()!= 'Q'):
            operands = command[1:]
            if len(operands)>1:
                URL = (f'http://127.0.0.1:8080/{cmd}?op1={operands[0]}&op2={operands[1]}')
                r = requests.get(URL)
                if (r.status_code == 200):
                    body = json.dumps(r.json(), indent=4)
                    content_dict = json.loads(body)
                    for k in content_dict.keys():
                        print("{}-->{}".format(k, content_dict[k]))
                else:
                    if r.status_code == 403:
                        print("ERROR:Zero division")
                    elif r.status_code == 404:
                        print("ERROR:Wrong Command")
                    elif r.status_code == 405:
                        print("ERROR:Empty Uri")
            else:
                print("ERROR:Lack of operands")



























