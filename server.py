import socket
import threading
from collections import defaultdict


shutdown_flag = False
clients = {}  # {username: socket}
groups = {}  # {group_name: {'members': set(), 'owner': username}}
lock = threading.Lock()


def broadcast(message, sender_socket=None):
    with lock:
        for username, client_socket in clients.items():
            if client_socket != sender_socket:
                try:
                    client_socket.send(message.encode())
                except:
                    del clients[username]


def handle_client(client_socket):
    username = ""
    try:
        # Get username
        user_reg = False
        while not user_reg:
            client_socket.send("Enter username: ".encode())
            username = client_socket.recv(1024).decode().strip()
            if username not in clients:
                user_reg = True
            else:
                client_socket.send("Username taken, try again\n".encode())

        with lock:
            clients[username] = client_socket

        broadcast(f"User {username} connected to the server", client_socket)

        while True:
            message = client_socket.recv(1024).decode()
            if not message:
                break

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
                            # Split the entire command, keeping the group name and member list together
                            _, group_and_members = message.split("@group set", 1)
                            group_and_members = group_and_members.strip()

                            # Now split the group name from the member list
                            parts = group_and_members.split(maxsplit=1)
                            if len(parts) < 2:
                                raise ValueError("Missing group name or members")

                            group_name = parts[0].strip().lower()
                            members_str = parts[1].strip()
                            members = [m.strip() for m in members_str.split(',') if m.strip()]

                            if not group_name:
                                raise ValueError("Group name cannot be empty")
                            if not members:
                                raise ValueError("Must specify at least one member")

                            with lock:
                                if group_name in groups:
                                    client_socket.send(f"Error: Group '{group_name}' already exists".encode())
                                    return

                                valid_members = [m for m in members if m in clients]
                                invalid_members = [m for m in members if m not in clients]

                                groups[group_name] = {
                                    'members': set(valid_members),
                                    'owner': username
                                }
                                for member in groups[group_name]['members']:
                                    clients[member].send(f"Group '{group_name}' created with members: {', '.join(valid_members)}".encode())

                                if invalid_members:
                                    response = f"\nWarning: Invalid members ignored: {', '.join(invalid_members)}"
                                    client_socket.send(response.encode())

                        except ValueError as e:
                            client_socket.send(
                                f"Error: {e}. Usage: @group set [group_name] [member1, member2, ...]".encode())
                        except Exception as e:
                            client_socket.send(f"Error processing group creation: {str(e)}".encode())

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
                                client_socket.send(f"Left group {group_name}".encode())
                                for member in groups[group_name]['members']:
                                    if member != username and member in clients:
                                        clients[member].send(f"[Group {group_name}] {username} left the group".encode())
                                    if groups[group_name]['owner'] == username:
                                        groups[group_name]['owner'] = groups[group_name]['members'][0]


                    elif subcmd == "delete":
                        group_name = group_parts[1]
                        with lock:
                            if group_name in groups and groups[group_name]['owner'] == username:
                                del groups[group_name]
                                client_socket.send(f"Deleted group {group_name}".encode())
                            else:
                                client_socket.send("Not authorized or group doesn't exist".encode())

                else:
                    client_socket.send("Invalid command".encode())

            else:
                broadcast(f"{username}: {message}", client_socket)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        with lock:
            if username in clients:
                del clients[username]
        broadcast(f"User {username} disconnected from server", client_socket)
        client_socket.close()


def server_program():
    global server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("0.0.0.0", 2222))
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

    with lock:
        for username, client_socket in clients.items():

            client_socket.send("SHUTDOWN".encode())
            client_socket.close()

        clients.clear()

    server.close()
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
