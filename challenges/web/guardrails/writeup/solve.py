import socket
import ssl
import requests

HOSTNAME = "ee803372-ae0a-40e5-a4c6-8c9a011832a4.chall.dev.nnsc.tf"
URL = f"https://{HOSTNAME}"

while True:
    # Use HTTPS for the requests
    r = requests.get(f"{URL}/store")  # Set verify=False for self-signed certificates
    print(r.text)

    # Create a secure socket connection
    context = ssl.create_default_context()
    sock = socket.create_connection((HOSTNAME, 443))
    secure_sock = context.wrap_socket(sock, server_hostname=HOSTNAME)

    # Send the POST request over the secure socket
    secure_sock.sendall(f"POST /store/flag HTTP/1.0\nHost: {HOSTNAME}\n\n".encode())
