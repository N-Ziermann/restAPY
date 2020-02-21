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
        # other
        self.debug = True


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
                try:
                    thread = threading.Thread(target=self.handle_https_request,name="thread",args=(secureSocket.accept()))
                    thread.daemon = True
                    thread.start()
                except:
                    if self.debug:
                        print("HTTP Request over HTTPS")
        else:
            raise Exception("Encryption is not turned on")


    def handle_https_request(self, clientsocket, address): # function for responding to api requests in a seperate thread
        requestString = clientsocket.recv(4096).decode("utf-8")
        try:
            request = htmlRequestToDict(requestString)
        except:
            if self.debug:
                print("Invalid Request")
            return
        request["Client-Info"] = address
        if request["Path"] in self.URLpaths:
            if type(self.URLpaths[request["Path"]]).__name__ != "function":
                jsonResponse = json.dumps(self.URLpaths[request["Path"]], indent=self.JSONindent, sort_keys=self.sortJSON)
            else:                   # if dev wants to do custom manipulation with his data
                response = self.URLpaths[request["Path"]](request)
                if response is None:
                    jsonResponse = json.dumps("Error no value to return. Please report to the administrator", indent=self.JSONindent, sort_keys=self.sortJSON)
                else:
                    jsonResponse = json.dumps(response, indent=self.JSONindent, sort_keys=self.sortJSON)
        else:
            self.send404(clientsocket)
            return

        clientsocket.send(b'HTTP/1.1 200 OK\n')
        clientsocket.send(b'Content-Type: application/json\n')
        clientsocket.send(b'\n')
        clientsocket.sendall(bytes(jsonResponse,self.encoding))
        clientsocket.close()


    def handle_http_request(self, clientsocket, address): # function for responding to api requests in a seperate thread
        requestString = clientsocket.recv(4096).decode("utf-8")
        try:
            request = htmlRequestToDict(requestString)
        except:
            if self.debug:
                print("Invalid Request")
            return
        request["Client-Info"] = address

        if self.redirectHttp and self.useTLS:
            redirect = "https://" + request["Host"] + request["Path"]
            clientsocket.send(b'HTTP/1.1 301 Moved Permanently\n')
            clientsocket.send(bytes('Location: ' + redirect + '\n', self.encoding))
            clientsocket.close()
        else:
            if request["Path"] in self.URLpaths:
                if type(self.URLpaths[request["Path"]]).__name__ != "function":
                    jsonResponse = json.dumps(self.URLpaths[request["Path"]], indent=self.JSONindent, sort_keys=self.sortJSON)
                else:                   # if dev wants to do custom manipulation with his data
                    response = self.URLpaths[request["Path"]](request)
                    if response is None:
                        jsonResponse = json.dumps("Error no value to return. Please report to the administrator", indent=self.JSONindent, sort_keys=self.sortJSON)
                    else:
                        jsonResponse = json.dumps(response, indent=self.JSONindent, sort_keys=self.sortJSON)
            else:
                self.send404(clientsocket)
                return

            clientsocket.send(b'HTTP/1.1 200 OK\n')
            clientsocket.send(b'Content-Type: application/json\n')
            clientsocket.send(b'\n')
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
    try:
        requestDict = {"Type":row1Data[0].strip(), "Path":row1Data[1].strip(), "JSON":""}
    except:
        raise Exception("Invalid Request")
    jsonStarted = False     # in case of post: tells code wether or not headers are done
    for i in range(1, len(rowSeperated)):
        if(rowSeperated[i] == "\r" or rowSeperated[i] == "\n"):
            jsonStarted = True
        if(len(rowSeperated[i])>1):
            key = ""
            value = ""
            j = 0
            if not jsonStarted:
                while rowSeperated[i][j] != ":":
                    key += rowSeperated[i][j]
                    j+=1
                j+=1    #skip ":"
                while j < len(rowSeperated[i]):
                    value += rowSeperated[i][j]
                    j+=1
                requestDict[key] = value.strip()
            else:
                requestDict["JSON"] += rowSeperated[i]
    return requestDict
