import socket
import threading
import hashlib
import os
import json

SERVER = ("0.0.0.0", 2222)
shutdown_flag = False
clients = {}  # {username: socket}
groups = {}  # {group_name: {'members': set(), 'owner': username}}
users = {}
lock = threading.Lock()
users_file = "users.txt"
groups_file = "groups.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_user():
    global users
    if os.path.exists(users_file):
        with open(users_file, "r") as f:
            for line in f:
                username, password_hash = line.strip().split(":")
                users[username] = password_hash

def save_user(username, password):
    with open(users_file, "a") as f:
        f.write(f"{username}:{hash_password(password)}\n")

def authenticate(client_socket):
    load_user()
    client_socket.send("Login (L) or Register (R): ".encode())
    choice = client_socket.recv(1024).decode().strip().lower()

    while choice not in ["l", "r"]:
        client_socket.send("Invalid choice. Please enter 'L' to login and 'R' to register: ".encode())
        choice = client_socket.recv(1024).decode().strip().lower()

    client_socket.send("Enter username: ".encode())
    username = client_socket.recv(1024).decode().strip()

    if choice == "r":
        if username in users:
            client_socket.send("Username already exists! Please try again.\n".encode())
            return None
        client_socket.send("Enter password: ".encode())
        password = client_socket.recv(1024).decode().strip()
        save_user(username, password)
        client_socket.send("Registration successful! You are now logged in.\n".encode())
    elif choice == "l":
        if username not in users:
            client_socket.send("User not found. Try again.\n".encode())
            return None
        client_socket.send("Enter password: ".encode())
        password = client_socket.recv(1024).decode().strip()
        if hash_password(password) != users[username]:
            client_socket.send("Incorrect password. Try again.\n".encode())
            return None
        client_socket.send("Login successful! Welcome.\n".encode())
    return username

def save_group():
    serializable_groups = {}
    for group_name, group_data in groups.items():
        serializable_groups[group_name] = {
            'members': list(group_data['members']),
            'owner': group_data['owner']
        }        
    with open(groups_file, "w") as f:
        json.dump(serializable_groups, f, indent=4)

def load_group():
    global groups
    if os.path.exists(groups_file):
        try:
            with open(groups_file, "r") as f:
                loaded_group = json.load(f)
                for group_name in loaded_group:
                    loaded_group[group_name]['members'] = set(loaded_group[group_name]['members'])
                groups = loaded_group
        except json.JSONDecodeError:
            print(f"Error loading groups file. Creating new empty groups dictionary")
            groups = {}
    else:
        print(f"Groups file not found. Creating new empty groups dictionary.")
        groups = {}

def broadcast(message, sender_socket=None):
    with lock:
        for username, client_socket in clients.items():
            if client_socket != sender_socket:
                try:
                    client_socket.send(message.encode())
                except:
                    del clients[username]


def handle_client(client_socket):
    global shutdown_flag, users
    username = None
    while username is None:
        username = authenticate(client_socket)

    if not username:
        client_socket.close()
        return
    with lock:
        clients[username] = client_socket
    broadcast(f"User {username} joined the chat!", client_socket)

    try:
        while not shutdown_flag:
            try:
                message = client_socket.recv(1024).decode()
                if not message:
                    break

                print(f"server received from {username}: {message}")

                # Command handling
                if message.startswith("@"):
                    parts = message.split(maxsplit=1)
                    command = parts[0][1:].lower()

                    # Quit command
                    if command == "quit":
                        break

                    # List users
                    elif command == "names":
                        with lock:
                            user_list = ", ".join(clients.keys())
                        client_socket.send(f"Connected users: {user_list}".encode())

                    # Private message
                    elif command in clients:
                        target_user = command
                        msg = parts[1] if len(parts) > 1 else ""
                        with lock:
                            if target_user in clients:
                                clients[target_user].send(f"(Private) {username}: {msg}".encode())
                            else:
                                client_socket.send("User not found".encode())

                    # Group commands
                    elif command == "group":
                        group_parts = parts[1].split(maxsplit=2)
                        subcmd = group_parts[0].lower()

                        if subcmd == "set":
                            try:
                                if len(group_parts) < 2:
                                    raise ValueError("Missing group name")
                                    
                                group_name = group_parts[1].lower()
                                members_str = " ".join(group_parts[2:]) if len(group_parts) > 2 else ""
                                members = [m.strip() for m in members_str.split(',') if m.strip()]
                                
                                if not members:
                                    client_socket.send("Error: Must specify at least one valid member\n".encode())
                                    continue
                                    
                                with lock:
                                    if group_name in groups:
                                        client_socket.send(f"Error: Group '{group_name}' already exists\n".encode())
                                        continue
                                        
                                    valid_members = [m for m in members if m in users]
                                    invalid_members = [m for m in members if m not in users]
                                    
                                    # Add the group creator to the members list if not already included
                                    if username not in valid_members:
                                        valid_members.append(username)
                                        
                                    groups[group_name] = {
                                        'members': set(valid_members),
                                        'owner': username
                                    }
                                    save_group()
                                    
                                    response = f"Group '{group_name}' created with members: {', '.join(valid_members)}\n"
                                    client_socket.send(response.encode())
                                    
                                    if invalid_members:
                                        client_socket.send(f"Warning: Invalid members ignored: {', '.join(invalid_members)}\n".encode())
                                        
                            except Exception as e:
                                client_socket.send(f"Error creating group: {str(e)}\n".encode())

                        elif subcmd == "send":
                                group_name = group_parts[1]
                                msg = group_parts[2]
                                with lock:
                                    if group_name in groups and username in groups[group_name]['members']:
                                        for member in groups[group_name]['members']:
                                            if member != username and member in clients:
                                                clients[member].send(f"[Group {group_name}] {username}: {msg}".encode())

                        elif subcmd == "leave":
                            group_name = group_parts[1]
                            with lock:
                                if group_name in groups and username in groups[group_name]['members']:
                                    groups[group_name]['members'].remove(username)
                                    save_group()
                                    client_socket.send(f"Left group {group_name}".encode())
                                    for member in groups[group_name]['members']:
                                        if member != username and member in clients:
                                            clients[member].send(f"[Group {group_name}] {username} left the group".encode())
                                    if groups[group_name]['owner'] == username and len(groups[group_name]['members'])==0:
                                        del groups[group_name]
                                        save_group()
                                    if groups[group_name]['owner'] == username and groups[group_name]['members']:
                                        groups[group_name]['owner'] = list(groups[group_name]['members'])[0]

                        elif subcmd == "kick":
                            try:
                                if len(group_parts) < 3:
                                    raise ValueError("Missing group name or members")
                                group_name = group_parts[1].lower()
                                members_str = " ".join(group_parts[2:])
                                members_to_kick = [m.strip() for m in members_str.split(',') if m.strip()]

                                if not members_to_kick:
                                    client_socket.send(
                                        "Error: Must specify at least one valid member to kick\n".encode())
                                    continue
                                with lock:
                                    if group_name not in groups:
                                        client_socket.send(f"Error: Group '{group_name}' does not exist\n".encode())
                                        continue
                                    if username != groups[group_name]['owner']:
                                        client_socket.send(
                                            f"Error: You must be the owner of group '{group_name}' to kick members\n".encode())
                                        continue
                                    valid_members = [m for m in members_to_kick if m in users and m != groups[group_name]['owner'] and m in groups[group_name]['members']]
                                    invalid_members = [m for m in members_to_kick if m not in users or m == groups[group_name]['owner']  and m not in groups[group_name]['members']]
                                    for member in valid_members:
                                        groups[group_name]['members'].remove(member)
                                    save_group()

                                    if invalid_members:
                                        client_socket.send(
                                            f"Warning: Invalid members ignored: {', '.join(invalid_members)}\n".encode())

                                    if invalid_members:
                                        for m in invalid_members:
                                            no_such_members = []
                                            not_in_group = []
                                            if m not in users:
                                                no_such_members.append(m)
                                            elif m not in groups[group_name]['members']:
                                                not_in_group.append(m)
                                        if no_such_members:
                                            client_socket.send(
                                                f"Warning: Invalid members ignored: {', '.join(no_such_members)}\n".encode())
                                        if not_in_group:
                                            client_socket.send(
                                                f"Warning: Cannot kick members {', '.join(not_in_group)} who are not in the group\n".encode())
                                    if valid_members:
                                        response = f"Kicked {', '.join(valid_members)} from '{group_name}'"
                                        client_socket.send(response.encode())

                                        # notify the person that is being kicked
                                        for kick_member in valid_members:
                                            if kick_member in clients and kick_member != username:
                                                clients[kick_member].send(f"You were removed from group '{group_name}' by {username}".encode())

                                        # notify group members
                                        notification = f"[Group {group_name}] {username} removed members: {', '.join(valid_members)}\n"
                                        for member in groups[group_name]['members']:
                                            if member != username and member in clients:
                                                clients[member].send(notification.encode())

                            except Exception as e:
                                client_socket.send(f"Error removing members from group: {str(e)}\n".encode())

                        elif subcmd == "delete":
                            group_name = group_parts[1]
                            with lock:
                                if group_name in groups and groups[group_name]['owner'] == username:
                                    del groups[group_name]
                                    save_group()
                                    client_socket.send(f"Deleted group {group_name}".encode())
                                else:
                                    client_socket.send("Not authorized or group doesn't exist".encode())

                        elif subcmd == "add":
                            try:
                                if len(group_parts) < 3:
                                    raise ValueError("Missing group name or members")
                                group_name = group_parts[1].lower()
                                members_str = " ".join(group_parts[2:])
                                members_to_add = [m.strip() for m in members_str.split(',') if m.strip()]

                                if not members_to_add:
                                    client_socket.send("Error: Must specify at least one valid member to add\n".encode())
                                    continue
                                with lock:
                                    if group_name not in groups:
                                        client_socket.send(f"Error: Group '{group_name}' does not exist\n".encode())
                                        continue
                                    #check if user is the owner of group chat to add member 
                                    if username != groups[group_name]['owner']:
                                        client_socket.send(f"Error: You must be the owner of group '{group_name}' to add members\n".encode())
                                        continue

                                    valid_members = [m for m in members_to_add if m in users and m not in groups[group_name]['members']]
                                    invalid_members = [m for m in members_to_add if m not in users or m in groups[group_name]['members']]
                                    groups[group_name]['members'].update(valid_members)
                                    save_group()

                                    if invalid_members:
                                        for m in invalid_members:
                                            no_such_members = []
                                            existing_members = []
                                            if m not in users:
                                                no_such_members.append(m)
                                            elif m in groups[group_name]['members']:
                                                existing_members.append(m)
                                        if no_such_members:
                                            client_socket.send(f"Warning: Invalid members ignored: {', '.join(no_such_members)}\n".encode())
                                        if existing_members:
                                            client_socket.send(f"Warning: Members: {', '.join(existing_members)} are already in the group\n".encode())
                                    if valid_members:
                                        response = f"Added {', '.join(valid_members)} into '{group_name}'"
                                        client_socket.send(response.encode())

                                        #notify group members
                                        notification = f"[Group {group_name}] {username} added new members: {', '.join(valid_members)}"
                                        for member in groups[group_name]['members']:
                                            if member != username and member in clients and member not in valid_members:
                                                clients[member].send(notification.encode())

                                        #notify the person that is being add
                                        for new_member in valid_members:
                                            if new_member in clients and new_member != username:
                                                clients[new_member].send(f"You were added to group '{group_name}' by {username}".encode())

                            except Exception as e:
                                client_socket.send(f"Error adding members to group: {str(e)}\n".encode())

                    else:
                        client_socket.send("Invalid command\n".encode())

                else:
                    broadcast(f"{username}: {message}", client_socket)
            except socket.error:
                if shutdown_flag:  # If we're shutting down, don't report the error
                    break
                raise
    except Exception as e:
        if not shutdown_flag:
            print(f"Exception: {e}\n")
    finally:
        with lock:
            if username in clients:
                del clients[username]
        if not shutdown_flag:  # Only broadcast disconnection if not shutting down
            broadcast(f"User {username} disconnected from server\n", client_socket)
        try:
            client_socket.close()
        except:
            pass


def server_program():
    load_group()
    global server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(SERVER)
        server.listen(5)
        server.settimeout(1)  # Set a timeout for the accept call

        print("Server started. Waiting for connections...")

        admin_thread = threading.Thread(target=admin_commands, daemon=True)
        admin_thread.start()

        while not shutdown_flag:
            try:
                client_socket, addr = server.accept()
                print(f"New connection from {addr}")
                client_thread = threading.Thread(target=handle_client, args=(client_socket,))
                client_thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                if shutdown_flag:
                    break
                print(f"Error accepting connections: {e}")

        admin_thread.join()  # Wait for admin thread to finish
        print("Server main loop exited")

def shutdown_server():
    global shutdown_flag
    shutdown_flag = True

    print("Shutting down server...")

    # Get all client sockets before clearing the dictionary
    client_sockets = []
    with lock:
        for username, client_socket in clients.items():
            client_sockets.append(client_socket)
            try:
                client_socket.send("SHUTDOWN".encode())  # Send shutdown signal
            except:
                pass

        clients.clear()

    # Close sockets after notifying all clients
    for client_socket in client_sockets:
        try:
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()
        except:
            pass

    # Wait a moment for threads to recognize the shutdown flag
    import time
    time.sleep(0.5)

    try:
        server.close()
    except:
        pass
    print("Server shut down gracefully")

def admin_commands():
    global shutdown_flag
    while not shutdown_flag:
        cmd = input("Server command: \n")
        if cmd.strip().lower() == "@shutdown":
            shutdown_server()
            break
    print("Admin command thread exited")

if __name__ == "__main__":
    server_program()
