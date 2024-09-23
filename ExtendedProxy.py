import socket
import ssl
import threading

SERVER_PORT = 80
CLIENT_IP = ''
CLIENT_PORT = 0
URL = ''
HOST = ''

context = ssl.create_default_context()


def is_socket_open(client_socket):
    try:
        # Attempt to retrieve the socket's error status
        error_code = client_socket.getsockopt(
            socket.SOL_SOCKET, socket.SO_ERROR)
        # If there is no error, the socket is open
        return error_code == 0
    except socket.error:
        # An exception occurred, indicating the socket is not open
        return False


def client_connection(client_socket):
    while is_socket_open(client_socket):

        # Receive and decode the client packet
        message = client_socket.recv(1024).decode()
        
        if not message or len(message.split(' ')) == 1:
            return
        
        # Extract the path portion of a URL from the first line of an HTTP request
        request_line = message.split('\r\n')[0]
        URL = request_line.split(' ')[1]
        
        # Parse the HTTP headers from an HTTP request message and store them in dictionary
        params = message.split('\r\n')[1:]
        req_params = {}
        for param in params:
            if param:
                key, value = param.split(': ', 1)
                req_params[key] = value
        
        SERVER_HOSTNAME = req_params["Host"]
        
        # Checking the incoming GET request and forwarding the same
        if request_line.split(' ')[0] == 'GET':
            data = server_connection(URL=URL, params=req_params)
            content_len = len(data)
            response = f"HTTP/1.1 200 OK\r\nDate: Fri, 04 Nov 2023 18:50:42 GMT\r\nServer: Proxy server\r\nContent-Length: {content_len}\r\nContent-Type: text/html\r\nConnection: Keep-Alive\r\n\r\n"

            headers = data.split(b'\r\n\r\n')[0]
            data = data[len(headers)+4:]
            client_socket.send(response.encode() + data)
            client_socket.send(b'harikrishnan_deepesh_priyanka')

        else:
            data = server_connection(URL, req_params, message)
            client_socket.close()


def server_connection(URL, params, request_forward=''):

    # Create connection with web server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Retrieving the hostname from the "Host" header in the HTTP request
    SERVER_HOSTNAME = params["Host"].split(':')[0]
    
    # Check the HTTP request port number
    if len(params["Host"].split(':')) == 2:
        SERVER_PORT = int(params["Host"].split(':')[1])
        if request_forward:
            SERVER_PORT = 80
    else:
        SERVER_PORT = 80
    
    # If port number == 443 then wrap the socket with SSL, if not use the regular socket for communication
    if SERVER_PORT == 443:
        default_context = ssl.create_default_context()
        server_socket_ssl = default_context.wrap_socket(
            server_socket, server_hostname=SERVER_HOSTNAME)
        server_socket_ssl.connect((SERVER_HOSTNAME, SERVER_PORT))
    else:
        server_socket.connect((SERVER_HOSTNAME, SERVER_PORT))
        server_socket_ssl = server_socket

    # Constructing the GET Request
    request = f"GET {URL} HTTP/1.1\r\nUser-Agent: Proxy Server\r\nHost: {SERVER_HOSTNAME}\r\nAccept-Language: en-us\r\nAccept-Encoding: utf-8\r\nConnection: Close\r\n\r\n"

    # Request for HTML file
    data = b''
    if request_forward:
        server_socket_ssl.send(bytes(request_forward, "utf-8"))
    else:
        server_socket_ssl.send(bytes(request, "utf-8"))
    while True:
        data1 = server_socket_ssl.recv(1024)
        data += data1
        if len(data1) == 0:
            break


    # Closing the sockets used for communications
    server_socket_ssl.close()

    # Return entire payload
    return data

# Create a new socket object
proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Assign IP address and port number to socket, with provision for 5 connections
proxy_socket.bind(('', 12000))

# Set up the socket to listen for incoming connections
proxy_socket.listen(5)
while True:

    # Accept an incoming connection on a listening socket.
    client_socket, address = proxy_socket.accept()

    # Creating a new thread to handle a client connection
    client_thread = threading.Thread(
        target=client_connection, args=(client_socket,))
    # Starts the thread
    client_thread.start()


# Accept connection from client
# Check if object is already present
# If object not present create server thread
# Return object with all referenced objects
