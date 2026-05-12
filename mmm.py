# import socket

# # Create a TCP/IP socket
# client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# # Connect to the server
# server_address = ('192.168.43.71', 9999)  # IP address of Raspberry Pi
# client_socket.connect(server_address)

# while True:
#     results = model(source='http://192.168.43.71:5000/video_feed', show=True, stream=True, conf=0.1)
#     for r in results:
#         masks = r.masks  # Masks object for segment masks outputs
#         if masks:
#             mask_data = masks.xyn  # Convert mask data to bytes or string
#             # Send mask data to the server
#             client_socket.sendall(mask_data.encode())
#         else:
#             print("no mask")

# # Close the connection
# client_socket.close()
