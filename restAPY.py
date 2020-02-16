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
        self.httpsPort = 443
        self.redirectHttp = True
        self.certchain = ""
        self.privkey = ""


    def setPath(self, path, data):
        self.URLpaths[path] = data


    def run(self):  # start connection listener loop
	if self.useTLS:
		thread = threading.Thread(target=self.https_listener)
		thread.daemon = True
		thread.start()
    self.http_listener()


    def http_listener(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.url, self.port))
        s.listen(self.maxConnections)
        while True:
            thread = threading.Thread(target=self.handle_http_request,name="thread",args=(s.accept()))
            thread.daemon = True
            thread.start()


    def https_listener(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.url, self.httpsPort))
        s.listen(self.maxConnections)
        if self.useTLS:
            if self.privkey == "":
                raise Exception("You need to set the privkey value to the location of your private key!")
            if(self.certchain == ""):
                raise Exception("You need to set the certchain value to the location of your certificate!")
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)#
            context.load_cert_chain(self.certchain, self.privkey)
            secureSocket = context.wrap_socket(s, server_side=True)
            while True:
                thread = threading.Thread(target=self.handle_https_request,name="thread",args=(secureSocket.accept()))
                thread.daemon = True
                thread.start()
        else:
            raise Exception("Encryption is not turned on")


    def handle_https_request(self, clientsocket, address): # function for responding to api requests in a seperate thread
        requestString = clientsocket.recv(4096).decode("utf-8")
        request = htmlRequestToDict(requestString)
        if request["Path"] in self.URLpaths:
            jsonResponse = json.dumps(self.URLpaths[request["Path"]], indent=self.JSONindent, sort_keys=self.sortJSON)
        else:
            self.send404(clientsocket)
            return

        if(request["Type"] == "GET"):   # http request
            clientsocket.send(b'HTTP/1.1 200 OK\n')
            clientsocket.send(b'Content-Type: application/json\n')
            clientsocket.send(b'\n')
            clientsocket.sendall(bytes(jsonResponse,self.encoding))
            clientsocket.close()
        else:                           # request made through something like the socket module
            clientsocket.sendall(bytes(jsonResponse,self.encoding))
            clientsocket.close()


    def handle_http_request(self, clientsocket, address): # function for responding to api requests in a seperate thread
        requestString = clientsocket.recv(4096).decode("utf-8")
        request = htmlRequestToDict(requestString)
        if self.redirectHttp:
            redirect = "https://" + request["Host"].strip() + request["Path"].strip()
            clientsocket.send(b'HTTP/1.1 301 Moved Permanently\n')
            clientsocket.send(bytes('Location: ' + redirect + '\n', self.encoding))
            clientsocket.close()
        else:
            if request["Path"] in self.URLpaths:
                jsonResponse = json.dumps(self.URLpaths[request["Path"]], indent=self.JSONindent, sort_keys=self.sortJSON)
            else:
                self.send404(clientsocket)
                return

            if(request["Type"] == "GET"):   # http request
                clientsocket.send(b'HTTP/1.1 200 OK\n')
                clientsocket.send(b'Content-Type: application/json\n')
                clientsocket.send(b'\n')
                clientsocket.sendall(bytes(jsonResponse,self.encoding))
                clientsocket.close()
            else:                           # request made through something like the socket module
                clientsocket.sendall(bytes(jsonResponse,self.encoding))
                clientsocket.close()


    def send404(self, client):              # sends 404 Error to client if something went wrong
        client.send(b'HTTP/1.1 404 Not Found\n')
        client.send(b'Content-Type: text/html\n')
        client.send(b'\n')
        client.sendall(b'404 Not Found')
        client.close()



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
