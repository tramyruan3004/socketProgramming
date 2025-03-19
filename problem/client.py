import socket
import threading
import sys
import select
isShutdown = False
SERVER = ('0.0.0.0', 2222)

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


def client_program():
    global isShutdown

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    client.connect(SERVER)

    username = input(client.recv(1024).decode())
    client.send(username.encode())

    authenticated = False
    while not authenticated and not isShutdown:
        auth_prompt = client.recv(1024).decode()
        print(auth_prompt, end='')

        auth_input = input()
        client.send(auth_input.encode())

        response = client.recv(1024).decode()
        print(response)

        if "successful" in response:
            authenticated = True

        # Continue with the existing message loop after authentication
        # ...rest of your client code...

    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

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
