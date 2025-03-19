import socket
import threading

# Server Configuration
HOST = '127.0.0.1'  
PORT = 12345        

def receive_messages(client):
    """Receive and display messages from the server."""
    while True:
        try:
            message = client.recv(1024).decode()
            print(message)
        except:
            print("Disconnected from server.")
            client.close()
            break

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    
    # Wait for the server's prompt
    prompt = client.recv(1024).decode()
    print(prompt, end="")  # Print the prompt without adding a newline

    # Get username from user
    username = input()
    client.send(username.encode())

    threading.Thread(target=receive_messages, args=(client,), daemon=True).start()

    while True:
        message = input()
        if message.startswith("@quit"):
            client.send(message.encode())
            break
        client.send(message.encode())

    client.close()

if __name__ == "__main__":
    main()