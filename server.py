import socket
import pickle  # Import pickle for deserialization

# Create a TCP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address and port
server_address = ('192.168.43.71', 9999)  # Use the IP of your Raspberry Pi
server_socket.bind(server_address)

# Listen for incoming connections
server_socket.listen(1)

print("Waiting for a connection...")

# Accept a connection
client_socket, client_address = server_socket.accept()

print("Connection established with:", client_address)

while True:
    # Receive mask data from the client
    mask_data = client_socket.recv(4096)  # Adjust buffer size as needed
    if not mask_data:
        break
    # Deserialize the received data
    masks = pickle.loads(mask_data)
    # Process the received mask data
    print("Received mask data:", masks)

# Close the connection
client_socket.close()
server_socket.close()
