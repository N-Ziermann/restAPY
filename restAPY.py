import socket
import threading
import time
import json

#turn into single API-Class later on


def run_api(port):  #while loop that starts a new thread for each incomming request
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind(("0.0.0.0", port))
    s.listen(16)
    print("listening on", "0.0.0.0", port )
    while True:
        thread = threading.Thread(target=handle_request,name="thread",args=(s.accept()))
        thread.daemon = True
        thread.start()


def handle_request(clientsocket, adress):
    requestString = clientsocket.recv(1024).decode("utf-8")
    request = htmlRequestToDict(requestString)
    jsonResponse = json.dumps({"a":"abc","b":5,"n":3}, indent=4, sort_keys=True)
    print(request)

    if(request["Type"] == "GET"):  # http request made through browser
        clientsocket.send(b'HTTP/1.0 200 OK\n')
        clientsocket.send(b'Content-Type: application/json\n')
        clientsocket.send(b'\n')
        clientsocket.sendall(bytes(jsonResponse,"utf-8"))
        clientsocket.close()
    else:
        clientsocket.sendall(bytes(jsonResponse,"utf-8"))
        clientsocket.close()


def htmlRequestToDict(request_string):
    rowSeperated = request_string.split("\n")
    requestDict = {"Type":rowSeperated[0].split(" ")[0]}
    for i in range(1, len(rowSeperated)):
        if(len(rowSeperated[i])>1): #prevent bugs caused by empty rows at end message
            key = ""
            value = ""
            j = 0
            while rowSeperated[i][j] != ":":
                key += rowSeperated[i][j]
                j+=1
            j+=1    #skip ":"
            while j < len(rowSeperated[i]):
                value += rowSeperated[i][j]
                j+=1
            requestDict[key] = value
    return requestDict
