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
            ###################################################################
            #  Cache handling
            ###################################################################
            cacheLocation = f'./{hostname}{resource}'
            if cacheLocation.endswith('/'):
                cacheLocation += 'default'
                
            # Cache validation and max-age handling
            cache_hit = False
            if os.path.isfile(cacheLocation):
                try:
                    file_mtime = os.path.getmtime(cacheLocation)
                    current_time = time.time()
                    valid_cache = True
                    
                    with open(cacheLocation, 'rb') as cacheFile:
                        cacheData = cacheFile.read()
                    
                    # Max-age validation
                    header_data = cacheData.split(b"\r\n\r\n", 1)[0]
                    headers = header_data.decode('utf-8', errors='replace')
                    for line in headers.split("\r\n"):
                        if line.lower().startswith("cache-control:"):
                            if 'max-age' in line:
                                max_age = int(re.search(r'max-age=(\d+)', line).group(1))
                                if current_time - file_mtime > max_age:
                                    valid_cache = False
                            break
                    
                    if valid_cache:
                        clientSocket.sendall(cacheData)
                        clientSocket.close()
                        cache_hit = True
                except Exception as e:
                    print('Cache error:', e)

            if cache_hit:
                continue

            ###################################################################
            #Origin server communication 
            ###################################################################
            originServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            originServerSocket.connect((socket.gethostbyname(hostname), 80))
            
            # Forward request
            origin_request = f"{method} {resource} {version}\r\nHost: {hostname}\r\nConnection: close\r\n\r\n"
            originServerSocket.sendall(origin_request.encode())

            # Receive response
            response_data = b''
            while True:
                chunk = originServerSocket.recv(BUFFER_SIZE)
                if not chunk: break
                response_data += chunk

