import socket
import sys
import ssl
from bs4 import BeautifulSoup
import os
import urllib.parse
import threading
import time


SERVER_PORT = 0
SERVER_HOST = ''
PROXY_HOST = ''
PROXY_PORT = 0
PATH = ''


def connect_to_server(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    return client_socket


def send_request(client_socket, request):
    client_socket.send(request.encode())


def receive_response(client_socket):
    response = b''
    while True:
        data = client_socket.recv(4096)
        if data[-29:] != b'harikrishnan_deepesh_priyanka':
            response = response + data
        else:
            client_socket.close()
            break
    # Save the index file
    file = open(os.path.join('downloaded_html', 'index.html'), 'wb')
    file.write(response.split(b'\r\n\r\n')[1])
    return response.decode()


def parse_html_for_references(html_content):
    referenced_objects = []

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        referenced_objects.append(href)

    # Find all <img> tags and get the 'src' attribute
    img_tags = soup.find_all('img')
    for img_tag in img_tags:
        src = img_tag.get('src')
        if src:
            referenced_objects.append(src)

    # Find all <link> tags and get the 'href' attribute
    link_tags = soup.find_all('link')
    for link_tag in link_tags:
        href = link_tag.get('href')
        if href:
            referenced_objects.append(href)

    return referenced_objects


def create_folder_to_save_assests():
    save_path = 'saved_assets'
    os.makedirs(save_path, exist_ok=True)
    return save_path


def create_folder_to_save_assests_Proxy():
    save_path = 'saved_assets_Proxy'
    os.makedirs(save_path, exist_ok=True)
    return save_path


def create_folder_to_save_HTML():
    save_HTML_path = 'downloaded_html'
    os.makedirs(save_HTML_path, exist_ok=True)
    return save_HTML_path


def create_folder_to_save_HTML_using_Proxy():
    save_HTML_path = 'downloaded_html_Proxy'
    os.makedirs(save_HTML_path, exist_ok=True)
    return save_HTML_path


def save_images(referenced_objects, save_path, thread_id,  SERVER_PORT=SERVER_PORT, SERVER_HOST=SERVER_HOST, PROXY_HOST='', PROXY_PORT=0):
    id = thread_id
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if PROXY_PORT > 0:
        client_socket.connect((PROXY_HOST, PROXY_PORT))
    else:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
    for i in range(len(referenced_objects)):
        if i == id:
            parsed_url = urllib.parse.urlparse(referenced_objects[i])
            filename = os.path.basename(parsed_url.path)
            id += 3
            request = f'GET {referenced_objects[i]} HTTP/1.0\r\nHost: {SERVER_HOST}:{SERVER_PORT}\r\nConnection: Keep-Alive\r\n\r\n'
            print(request)
            client_socket.sendall(request.encode())
            response = b""
            while True:
                data = client_socket.recv(4096)
                if data[-29:] != b'harikrishnan_deepesh_priyanka':
                    response = response + data
                else:
                    break
            headers = response.split(b'\r\n\r\n')[0]
            data = response[len(headers)+4:]

            # Save the image content to a file
            file = open(os.path.join(save_path, filename), 'wb')
            file.write(data)
            file.close()
            print(
                f"File {filename} downloaded successfully with thread id {thread_id}")
    client_socket.close()


def download_image(url, save_path, client_socket, SERVER_PORT, SERVER_HOST, PROXY_HOST, PROXY_PORT):

    # Parse the URL to get the filename
    parsed_url = urllib.parse.urlparse(url)
    filename = os.path.basename(parsed_url.path)

    # if port == 443:
    #     # Wrap the socket with SSL
    #     context = ssl.create_default_context()
    #     client_socket = context.wrap_socket(client_socket, server_hostname=host)

    # Send a GET request to download the image
    request = f'GET {url} HTTP/1.0\r\nHost: {SERVER_HOST}:{SERVER_PORT}\r\nConnection: Keep-Alive\r\n\r\n'

    client_socket.sendall(request.encode())
    response = b""
    while True:
        data = client_socket.recv(4096)
        if data[-29:] != b'harikrishnan_deepesh_priyanka':
            response = response + data
        else:
            break

    headers = response.split(b'\r\n\r\n')[0]
    data = response[len(headers)+4:]

    # Save the image content to a file
    file = open(os.path.join(save_path, filename), 'wb')
    file.write(data)
    file.close()


def main():
    # if len(sys.argv) != 4:
    #     print("Usage: python web_client.py <host> <port> <path>")
    #     sys.exit(1)
    start = time.time()
    if len(sys.argv) == 4:
        SERVER_HOST = sys.argv[1]
        SERVER_PORT = int(sys.argv[2])
        PATH = sys.argv[3]

        # connect to server
        client_socket = connect_to_server(SERVER_HOST, SERVER_PORT)

        if SERVER_PORT == 443:
            # Wrap the socket with SSL
            context = ssl.create_default_context()
            client_socket = context.wrap_socket(
                client_socket, server_hostname=SERVER_HOST)

        # Send HTTP GET request
        request = f"GET {PATH} HTTP/1.0\r\nHost: {SERVER_HOST}:{SERVER_PORT}\r\n\r\n"

        # Send Request
        send_request(client_socket, request)

        # Create a folder to Save HTML File
        save_HTML_path = create_folder_to_save_HTML()

        # Recieve Response
        response = receive_response(client_socket)
        print(response)
        client_socket.close()

        # Parse the HTML for references
        referenced_objects = parse_html_for_references(response)
        print("referenced_objects", referenced_objects)

        # Create a folder to Save Assests
        save_path = create_folder_to_save_assests()

        objects_dict = {}

        for i in range(len(referenced_objects)):
            objects_dict[i] = referenced_objects[i]

        # Save Images in a Particular Directory
        thread_1 = threading.Thread(target=save_images, args=(
            objects_dict, save_path, 0, SERVER_PORT, SERVER_HOST,))
        thread_2 = threading.Thread(target=save_images, args=(
            objects_dict, save_path, 1, SERVER_PORT, SERVER_HOST,))
        thread_3 = threading.Thread(target=save_images, args=(
            objects_dict, save_path, 2, SERVER_PORT, SERVER_HOST,))
        thread_1.start()
        thread_2.start()
        thread_3.start()

    elif len(sys.argv) == 6:

        PROXY_HOST = sys.argv[1]
        PROXY_PORT = int(sys.argv[2])
        SERVER_HOST = sys.argv[3]
        SERVER_PORT = int(sys.argv[4])
        PATH = sys.argv[5]

        # Send HTTP GET request
        request = f"GET {PATH} HTTP/1.0\r\nHost: {SERVER_HOST}:{SERVER_PORT}\r\n\r\n"

        # connect to server
        proxy_socket = connect_to_server(PROXY_HOST, PROXY_PORT)

        # Send Request
        send_request(proxy_socket, request)

        # Create a folder to Save HTML File
        save_HTML_path = create_folder_to_save_HTML_using_Proxy()

        # Recieve Response
        response = receive_response(proxy_socket)
        print(response)
        proxy_socket.close()

        # Parse the HTML for references
        referenced_objects = parse_html_for_references(response)
        print("referenced_objects", referenced_objects)

        # Create a folder to Save Assests
        save_path = create_folder_to_save_assests_Proxy()

        objects_dict = {}

        suffixes_to_check = ['.jpg', '.jpeg',
                             '.png', '.gif', '.css', '.txt', '.pdf']

        referenced_objects = [obj for obj in referenced_objects if any(
            obj.endswith(suffix) for suffix in suffixes_to_check)]

        for i in range(len(referenced_objects)):
            objects_dict[i] = referenced_objects[i]

        # Save Images in a Particular Directory
        thread_1 = threading.Thread(target=save_images, args=(
            objects_dict, save_path, 0, SERVER_PORT, SERVER_HOST, PROXY_HOST, PROXY_PORT))
        thread_2 = threading.Thread(target=save_images, args=(
            objects_dict, save_path, 1, SERVER_PORT, SERVER_HOST, PROXY_HOST, PROXY_PORT))
        thread_3 = threading.Thread(target=save_images, args=(
            objects_dict, save_path, 2, SERVER_PORT, SERVER_HOST, PROXY_HOST, PROXY_PORT))

        thread_1.start()
        thread_2.start()
        thread_3.start()

        thread_1.join()
        thread_2.join()
        thread_3.join()

    else:
        print("Usage: python web_client.py <host> <port> <path>")
        sys.exit(1)

    end = time.time()
    print(f"Time taken for servicing request: {(end -start) * 1000} ms.")


main()
