import socket
import threading
import sys
import select
isShutdown = False

SERVER = ('192.168.1.147', 2222)

def receive_messages(client_socket):
    global isShutdown  # Ensure this affects the main thread
    while not isShutdown:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                print("Server disconnected.")
                isShutdown = True
                break
            if message == "SHUTDOWN":
                print("Server is shutting down.")
                isShutdown = True  # Signal the main thread to stop
                break
            print(message)
        except socket.error:
            print("Lost connection to server.")
            isShutdown = True
            break

def send_messages(client_socket):
    global isShutdown
    while not isShutdown:
        try:
            message = input()
            if message.lower() == '@quit':
                print("Disconnecting from server...")
                isShutdown = True
                client_socket.sendall(message.encode())
                client_socket.close()
                break
            client_socket.sendall(message.encode())
        except:
            break

def client_program():
    global isShutdown

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(SERVER)

    username = input(client.recv(1024).decode())
    client.send(username.encode())

    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    send_thread = threading.Thread(target=send_messages, args=(client,))
    send_thread.start()

    receive_thread.join()
    send_thread.join()

    try:
        while not isShutdown:  # Keep checking if we need to shut down
            readable, _, _ = select.select([sys.stdin], [], [], 0.1)

            if client in readable:  # Server sent a message
                message = client.recv(1024).decode()
                if not message or message == "SHUTDOWN":
                    print("Server is shutting down.")
                    isShutdown = True
                    break  # Exit loop
                print(message)

            if sys.stdin in readable:  # User input is available
                message = input()  # Use input() instead of sys.stdin.readline()
                if message.lower() == '@quit':
                    isShutdown = True
                    break
                if message:
                    print(f"Sending: {message}")
                    client.sendall(message.encode())

    finally:
        client.close()
        receive_thread.join()
    print("Disconnected from server.")


if __name__ == '__main__':
    client_program()
