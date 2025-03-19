import socket
import threading

# Server Configuration
HOST = '127.0.0.1'  # Localhost
PORT = 12345

# Store connected clients and usernames
clients = {}
groups = {}

def broadcast(message, sender=None):
    """Send message to all connected clients."""
    for user, client in clients.items():
        if user != sender:
            client.send(message.encode())

def handle_client(client, username):
    """Handle communication with a client."""
    try:
        while True:
            message = client.recv(1024).decode()
            if message.startswith('@quit'):
                broadcast(f"{username} has left the chat.", username)
                del clients[username]
                break
            elif message.startswith('@names'):
                client.send(f"Connected users: {', '.join(clients.keys())}".encode())
            elif message.startswith('@group set'):
                _, group_name, *members = message.split()
                groups[group_name] = set(members)
                client.send(f"Group {group_name} created.".encode())
            elif message.startswith('@group send'):
                _, group_name, *msg = message.split()
                msg_text = ' '.join(msg)
                if group_name in groups:
                    for user in groups[group_name]:
                        if user in clients:
                            clients[user].send(f"[Group {group_name}] {username}: {msg_text}".encode())
            elif message.startswith('@group leave'):
                _, group_name = message.split()
                if group_name in groups and username in groups[group_name]:
                    groups[group_name].remove(username)
                    client.send(f"You left group {group_name}".encode())
            else:
                broadcast(f"{username}: {message}", username)
    except:
        pass
    finally:
        client.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print("Server started...")
    
    while True:
        client, addr = server.accept()
        client.send("Enter username: ".encode())
        username = client.recv(1024).decode().strip()  # Use .strip() to remove extra whitespace
        if username in clients:
            client.send("Username already taken!".encode())
            client.close
            continue
        clients[username] = client
        print(f"{username} connected from {addr}")
        broadcast(f"{username} joined the chat!", username)
        threading.Thread(target=handle_client, args=(client, username)).start()

if __name__ == "__main__":
    main()