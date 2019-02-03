#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
# you may use urllib to encode data appropriately
from urllib.parse import urlparse, urlencode

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=500, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        # print("Connected")
        return self.socket

    def get_code(self, data):
        code = data.split()[1]
        # print("Code: ", code)
        return int(code)

    def get_body(self, data):
        body = data.split("\r\n\r\n")[1]
        return body

    def get_response(self, request):
        sock = self.connect()
        self.sendall(request)
        data = self.recvall(sock)
        self.close()
        return data

    # From https://docs.python.org/3/library/urllib.parse.html
    def parse_url(self, url):
        parsed_url = urlparse(url)
        self.host_name = parsed_url.netloc
        self.host = parsed_url.netloc.split(":")[0]
        self.port = parsed_url.port
        self.path = parsed_url.path
        if (self.path == ""):
            self.path = "/"
        if (self.port == None):
            self.port = 80
        # print(self.host, "Host")
        # print(self.host_name, "HN")
        # print("port", self.port)
        # print("Path:", self.path)

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        self.parse_url(url)
        request = f"GET {self.path} HTTP/1.1\r\nHost: {self.host_name}\r\n\r\n"
        data = self.get_response(request)

        code = self.get_code(data)
        body = self.get_body(data)
        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        body = ""
        self.parse_url(url)
        if (args != None):
            # From https://stackoverflow.com/questions/4163263/transferring-dictionary-via-post-request
            body = urlencode(args)
        # From https://realpython.com/python-f-strings/#f-strings-a-new-and-improved-way-to-format-strings-in-python
        length = f"\nContent-Length: {len(body)}"
        request = f"POST {self.path} HTTP/1.1\r\nHost: {self.host_name}\nContent-Type: application/x-www-form-urlencoded{length}\r\n\r\n{body}"
        
        data = self.get_response(request)

        code = self.get_code(data)
        body = self.get_body(data)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
