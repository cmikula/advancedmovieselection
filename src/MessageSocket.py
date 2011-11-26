#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Copyright (C) 2011 cmikula

In case of reuse of this source code please do not remove this copyright.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    For more information on the GNU General Public License see:
    <http://www.gnu.org/licenses/>.

For example, if you distribute copies of such a program, whether gratis or for a fee, you 
must pass on to the recipients the same freedoms that you received. You must make sure 
that they, too, receive or can get the source code. And you must show them these terms so they know their rights.
'''

import SocketServer
import socket
from MessageQueue import MessageQueue

instance = None

def getIpAddress(iface):
    interfaces = []
    # parse the interfaces-file
    try:
        fp = file('/etc/network/interfaces', 'r')
        interfaces = fp.readlines()
        fp.close()
    except:
        print "interfaces - opening failed"

    currif = ""
    for i in interfaces:
        split = i.strip().split(' ')
        if (split[0] == "iface"):
            currif = split[1]
        if (currif == iface): #read information only for available interfaces
            if (split[0] == "address"):
                return split[1]
    return None

class TCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        data = self.request.recv(1024).strip()
        print str(self.client_address[0]), "wrote"
        print data
        self.request.send(MessageQueue.getRequest(data))

class MessageSocketServer():
    def __init__(self):
        global instance
        if instance:
            raise Exception("Only one instance of MessageSocketServer is allowed")
        self.server = None
        self.active_clients = []
        self.host = getIpAddress('eth0')
        self.port = 9999

    def start(self):
        if not self.host:
            print "Could not start server, no static host ip"
            return
        import threading
        if self.server:
            self.server.shutdown()
        self.server = SocketServer.TCPServer((self.host, self.port), TCPHandler)
        self.t = threading.Thread(target=self.server.serve_forever)
        self.t.setDaemon(True) # don't hang on exit
        self.t.start()
        print "Server started:", self.host, self.port
        
    def reconnect(self, host=None, port=None):
        if host:
            self.host = host
        if port:
            self.port = port
        self.start()
        
    def getHost(self):
        return self.host
    
    def getPort(self):
        return self.port

    def findClients(self):
        self.active_clients = []
        if not self.server:
            return
        ip = self.host.split(".")
        ip = "%s.%s.%s" % (ip[0], ip[1], ip[2])
        for x in range(1, 255):
            try:
                # Connect to server and send data
                host = "%s.%s" % (ip, x)
                #print "Try connect to:", host
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)
                sock.connect((host, self.port))
                self.active_clients.append(host)
            except:
                pass
            finally:
                sock.close()
        
    def startScanForClients(self):
        import threading
        t = threading.Thread(target=self.findClients)
        t.start()
        
    def getClients(self):
        return self.active_clients
        
instance = MessageSocketServer()

class MessageSocketClient:
    @staticmethod
    def getRequest(host, port, data):
        request = data
        try:
            # Connect to server and send data
            print "Send message to:", host
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((host, port))
            sock.send(data)
            # Receive data from the server and shut down
            request = sock.recv(1024)
            print "Get request:", request
        except:
            pass
        finally:
            sock.close()
        return request
