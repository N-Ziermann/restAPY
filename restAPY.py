import socket
import threading
import json
import ssl

class API:
    def __init__(self, port=80, url="0.0.0.0"):
        # connection info:
        self.port = port
        self.url = url
        self.max_connections = 16
        self.encoding = "utf-8"
        # JSON settings
        self.url_paths = {"/" : {"info": ["Default data", "No data given"]}}
        self.sort_json = False
        self.json_indent = 4
        # encryption (https)
        self.use_tls = False
        self.https_port = 443
        self.redirect_http = True
        self.certchain = ""
        self.privkey = ""
        # other
        self.debug = True


    def set_path(self, path, data):
        self.url_paths[path] = data


    def run(self):  # start connection listener loop
        if self.use_tls:
            thread = threading.Thread(target=self.https_listener)
            thread.daemon = True
            thread.start()
        self.http_listener()



    def http_listener(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.url, self.port))
        s.listen(self.max_connections)
        while True:
            thread = threading.Thread(target=self.handle_http_request,name="thread",args=(s.accept()))
            thread.daemon = True
            thread.start()


    def https_listener(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.url, self.https_port))
        s.listen(self.max_connections)
        if self.use_tls:
            if self.privkey == "":
                raise Exception("You need to set the privkey value to the location of your private key!")
            if(self.certchain == ""):
                raise Exception("You need to set the certchain value to the location of your certificate!")
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)#
            context.load_cert_chain(self.certchain, self.privkey)
            secure_socket = context.wrap_socket(s, server_side=True)
            while True:
                try:
                    thread = threading.Thread(target=self.handle_https_request,name="thread",args=(secure_socket.accept()))
                    thread.daemon = True
                    thread.start()
                except:
                    if self.debug:
                        print("HTTP Request over HTTPS")
        else:
            raise Exception("Encryption is not turned on")


    def handle_https_request(self, clientsocket, address): # function for responding to api requests in a seperate thread
        request_string = clientsocket.recv(4096).decode("utf-8")
        try:
            request = html_request_to_dict(request_string)
        except:
            if self.debug:
                print("Invalid Request")
            return
        request["Client-Info"] = address
        if request["Path"] in self.url_paths:
            if type(self.url_paths[request["Path"]]).__name__ != "function":
                json_response = json.dumps(self.url_paths[request["Path"]], indent=self.json_indent, sort_keys=self.sort_json)
            else:                   # if dev wants to do custom manipulation with his data
                response = self.url_paths[request["Path"]](request)
                if response is None:
                    json_response = json.dumps("Error no value to return. Please report to the administrator", indent=self.json_indent, sort_keys=self.sort_json)
                else:
                    json_response = json.dumps(response, indent=self.json_indent, sort_keys=self.sort_json)
        else:
            self.send_404(clientsocket)
            return

        clientsocket.send(b'HTTP/1.1 200 OK\n')
        clientsocket.send(b'Content-Type: application/json\n')
        clientsocket.send(b'\n')
        clientsocket.sendall(bytes(json_response,self.encoding))
        clientsocket.close()


    def handle_http_request(self, clientsocket, address): # function for responding to api requests in a seperate thread
        request_string = clientsocket.recv(4096).decode("utf-8")
        try:
            request = html_request_to_dict(request_string)
        except:
            if self.debug:
                print("Invalid Request")
            return
        request["Client-Info"] = address

        if self.redirect_http and self.use_tls:
            redirect = "https://" + request["Host"] + request["Path"]
            clientsocket.send(b'HTTP/1.1 301 Moved Permanently\n')
            clientsocket.send(bytes('Location: ' + redirect + '\n', self.encoding))
            clientsocket.close()
        else:
            if request["Path"] in self.url_paths:
                if type(self.url_paths[request["Path"]]).__name__ != "function":
                    json_response = json.dumps(self.url_paths[request["Path"]], indent=self.json_indent, sort_keys=self.sort_json)
                else:                   # if dev wants to do custom manipulation with his data
                    response = self.url_paths[request["Path"]](request)
                    if response is None:
                        json_response = json.dumps("Error no value to return. Please report to the administrator", indent=self.json_indent, sort_keys=self.sort_json)
                    else:
                        json_response = json.dumps(response, indent=self.json_indent, sort_keys=self.sort_json)
            else:
                self.send_404(clientsocket)
                return

            clientsocket.send(b'HTTP/1.1 200 OK\n')
            clientsocket.send(b'Content-Type: application/json\n')
            clientsocket.send(b'\n')
            clientsocket.sendall(bytes(json_response,self.encoding))
            clientsocket.close()


    def send_404(self, client):              # sends 404 Error to client if something went wrong
        client.send(b'HTTP/1.1 404 Not Found\n')
        client.send(b'Content-Type: text/html\n')
        client.send(b'\n')
        client.sendall(b'404 Not Found')
        client.close()



def html_request_to_dict(request_string):  # makes requests from webbrowsers easier to work with
    row_seperated = request_string.split("\n")
    row_1_data = row_seperated[0].split(" ")
    try:
        request_dict = {"Type":row_1_data[0].strip(), "Path":row_1_data[1].strip(), "JSON":""}
    except:
        raise Exception("Invalid Request")
    json_started = False     # in case of post: tells code wether or not headers are done
    for i in range(1, len(row_seperated)):
        if(row_seperated[i] == "\r" or row_seperated[i] == "\n"):
            json_started = True
        if(len(row_seperated[i])>1):
            key = ""
            value = ""
            j = 0
            if not json_started:
                while row_seperated[i][j] != ":":
                    key += row_seperated[i][j]
                    j+=1
                j+=1    #skip ":"
                while j < len(row_seperated[i]):
                    value += row_seperated[i][j]
                    j+=1
                request_dict[key] = value.strip()
            else:
                request_dict["JSON"] += row_seperated[i]
    return request_dict
