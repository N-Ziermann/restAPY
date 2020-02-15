import socket
import threading
import json
import ssl

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
        # encryption (https)
        self.useTLS = False
        self.certchain = ""
        self.privkey = ""


    def setPath(self, path, data):
        self.URLpaths[path] = data


    def run(self):  # start connection listener loop
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.bind((self.url, self.port))
        self.socket.listen(self.maxConnections)
        print("listening on", self.url, self.port )
        if(self.useTLS): # encrypted
            if(self.privkey == ""):
                raise Exception("You need to set the privkey value to the location of your private key!")
            if(self.certchain == ""):
                raise Exception("You need to set the certchain value to the location of your certificate!")
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(self.certchain, self.privkey)
            self.secureSocket = context.wrap_socket(self.socket, server_side=True)
            while True:
                thread = threading.Thread(target=self.handle_request,name="thread",args=(self.secureSocket.accept()))
                thread.daemon = True
                thread.start()
        else:
            while True:
                thread = threading.Thread(target=self.handle_request,name="thread",args=(self.socket.accept()))
                thread.daemon = True
                thread.start()


    def handle_request(self, clientsocket, address): # function for responding to api requests in a seperate thread
        requestString = clientsocket.recv(4096).decode("utf-8")
        request = htmlRequestToDict(requestString)
        if request["Path"] in self.URLpaths:
            jsonResponse = json.dumps(self.URLpaths[request["Path"]], indent=self.JSONindent, sort_keys=self.sortJSON)
        else:
            jsonResponse = json.dumps({"Error":"Invalid Path"})

        if(request["Type"] == "GET"):   # http request
            clientsocket.send(b'HTTP/1.1 200 OK\n')
            clientsocket.send(b'Content-Type: application/json\n')
            clientsocket.send(b'\n')
            clientsocket.sendall(bytes(jsonResponse,self.encoding))
            clientsocket.close()
        else:                           # request made through something like the socket module
            clientsocket.sendall(bytes(jsonResponse,self.encoding))
            clientsocket.close()



def htmlRequestToDict(request_string):  # makes requests from webbrowsers easier to work with
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
