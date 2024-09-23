import socket
import threading
import os
import urllib

# Configuration
HOST = '127.0.0.1'  # Listen on all available network interfaces
PORT = 9000
DOC_ROOT = os.getcwd()  # Use the current working directory as the document root
def handle_client(client_socket):
    request = client_socket.recv(1024).decode()  # Receive and decode the HTTP request
    filename = parse_request(request)

    if filename:
        response = serve_file(filename)
        client_socket.send(response)
        client_socket.close()
    else:
        response = "HTTP/1.1 404 Not Found\r\n\r\n404 Not Found"
        client_socket.send(response.encode())
        client_socket.close()
        
        

    

def parse_request(request):
    try:
        filename = request.split(' ')[1]
        if filename[0]=='/':
            return filename[1:]
        return filename
    except Exception as e:
        return None

def serve_file(filename):
    try:
        with open(os.path.join(DOC_ROOT, filename), 'rb') as file:
            content = file.read()
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                response = b"HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\n\r\n" + content
            else:
                response = b"HTTP/1.1 200 OK\r\n\r\n" + content
            print(filename+ " sent.")
            return response
    except FileNotFoundError:
        return "HTTP/1.1 404 Not Found\r\n\r\n404 Not Found".encode()
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Listening on {HOST}:{PORT}")

    while True:
        client, addr = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client,))
        print("Connection established ")
        client_thread.start()

if __name__ == '__main__':
    main()