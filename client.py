import socket
import threading


def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                print("Server disconnected.")
                break
            if message == "SHUTDOWN":
                print("Server is shutting down.")
                break
            print(message)
        except socket.error:
            print("Lost connection to server.")
            break



def client_program():
    host = '0.0.0.0'  # Use server IP
    port = 2222

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    username = input(client.recv(1024).decode())
    client.send(username.encode())

    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    try:
        while True:
            message = input()
            if message.lower() == '@quit':
                break
            try:
                client.send(message.encode())
            except socket.error:
                print("Lost connection to server.")
                break
    finally:
        client.close()
        receive_thread.join()  # Wait for receive thread to finish
    print("Disconnected from server.")


if __name__ == '__main__':
    client_program()
