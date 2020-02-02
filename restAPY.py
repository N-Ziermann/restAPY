import socket
import threading
import time
import json

#turn into single API-Class later on

class API:
    def __init__(self, port=80, url="0.0.0.0"):
        # connection info:
        self.port = port
        self.url = url
        self.maxConnections = 16
        self.encoding = "utf-8"
        # JSON settings
        self.URLpaths = {"/" : {"info": ["Default data", "No data given"]}}
        self.sortJSON = False
        self.JSONindent = 4


    def setPath(self, path, data):
        self.URLpaths[path] = data


    def run(self):
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.bind((self.url, self.port))
        self.socket.listen(self.maxConnections)
        print("listening on", self.url, self.port )
        while True:
            thread = threading.Thread(target=self.handle_request,name="thread",args=(self.socket.accept()))
            thread.daemon = True
            thread.start()


    def handle_request(self, clientsocket, adress):
        requestString = clientsocket.recv(1024).decode("utf-8")
        request = htmlRequestToDict(requestString)
        if request["Path"] in self.URLpaths:
            jsonResponse = json.dumps(self.URLpaths[request["Path"]], indent=self.JSONindent, sort_keys=self.sortJSON)
        else:
            jsonResponse = "Invalid Path"

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
    row1Data = rowSeperated[0].split(" ")
    requestDict = {"Type":row1Data[0], "Path":row1Data[1]}
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
