#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, Carlo Oliva
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
from urllib.parse import *


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):

    def __init__(self):
        self.socket = None

    def get_host_port(self, url):
        # Taken from https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlparse on January 31, 2019
        o = urlparse(url)

        if ':' in o.netloc:
            host = o.netloc.split(":")[0]
            port = int(o.netloc.split(":")[1])
        else:
            host = o.netloc
            port = 80

        return host, port

    def get_path(self, url):
        # Taken from https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlparse on January 31, 2019
        o = urlparse(url)
        if not o.path:
            return "/"
        else:
            return o.path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = data.split("\r\n")[0].split(" ")[1]
        return int(code)

    def get_headers(self, data):
        headers = data.split("\r\n\r\n")
        return headers[0]

    def get_body(self, data):
        body = data.split("\r\n\r\n")
        if len(body) < 2:
            body = ''
        else:
            body = body[1]

        return body

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

    @staticmethod
    def _generate_request(http_method, host, path, args):
        carriage_newline = '\r\n'

        # Add Http method
        req = '{} {} HTTP/1.1{}'.format(http_method, path, carriage_newline)

        # Add Host header
        req += 'Host: {}{}'.format(host, carriage_newline)

        # Add User Agent
        # Taken from https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent on Feb 2, 2018
        req += 'User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0{}'.format(
            carriage_newline)

        # Add Accept header
        # Taken from https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html
        req += 'Accept: text/*, text/html, text/html;level=1, */*{}'.format(carriage_newline)

        req += 'Content-Type: application/x-www-form-urlencoded{}'.format(carriage_newline)

        # Add Content Type if POST
        # Taken from https://code.tutsplus.com/tutorials/http-headers-for-dummies--net-8039
        if http_method == 'POST':
            # Add Content Length and data
            if args:
                req += 'Content-Length: {}{}'.format(len(urlencode(args)), carriage_newline)
                req += carriage_newline
                req += urlencode(args)
                req += carriage_newline * 2
            else:
                req += 'Content-Length: 0{}'.format(carriage_newline)
                req += carriage_newline * 2

        else:
            req += carriage_newline

        return req

    def GET(self, url, args=None):
        host, port = self.get_host_port(url)
        path = self.get_path(url)
        req = self._generate_request('GET', host, path, args)
        self.connect(host, port)
        self.sendall(req)

        # Taken from Lab 2 CMPUT 404 Winter 2019
        self.socket.shutdown(socket.SHUT_WR)

        resp = self.recvall(self.socket)

        print(resp)
        self.close()
        code = self.get_code(resp)
        body = self.get_body(resp)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port = self.get_host_port(url)
        path = self.get_path(url)
        self.connect(host, port)
        req = self._generate_request('POST', host, path, args)
        self.sendall(req)

        # Taken from Lab 2 CMPUT 404 Winter 2019
        self.socket.shutdown(socket.SHUT_WR)

        resp = self.recvall(self.socket)
        print(resp)

        self.close()
        code = self.get_code(resp)
        body = self.get_body(resp)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
