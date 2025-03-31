import socket
import sys
import os
import argparse
import re
import time

BUFFER_SIZE = 1000000

def main():
    ###################################################################
    # Proxy server started
    ###################################################################
    parser = argparse.ArgumentParser()
    parser.add_argument('hostname', help='the IP Address Of Proxy Server')
    parser.add_argument('port', help='the port number of the proxy server')
    args = parser.parse_args()
    proxyHost = args.hostname
    proxyPort = int(args.port)

    # Socket setup
    try:
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind((proxyHost, proxyPort))
        serverSocket.listen(50)
        print('Proxy server started')
    except Exception as e:
        print('Server startup failed:', e)
        sys.exit()
    while True:
        ###################################################################
        # Connected to Proxy server
        ###################################################################
        try:
            clientSocket, clientAddress = serverSocket.accept()
            print(f'Connection from: {clientAddress}')
        except Exception as e:
            print('Connection failed:', e)
            continue

        try:
            message_bytes = clientSocket.recv(BUFFER_SIZE)
            if not message_bytes:
                clientSocket.close()
                continue

            ###################################################################
            #  Obtained remote homepage/file
            ###################################################################
            message = message_bytes.decode('utf-8', errors='replace')
            request_line = message.split('\r\n')[0]
            method, URI, version = request_line.split()
            
            # URI parsing
            URI = URI.lstrip('/')
            URI = re.sub('^http(s?)://', '', URI, count=1)
            resourceParts = URI.split('/', 1)
            hostname = resourceParts[0]
            resource = '/' + resourceParts[1] if len(resourceParts) == 2 else '/'

