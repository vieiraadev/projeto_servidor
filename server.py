import socket
import threading

HOST = '0.0.0.0'
PORT = 12345

clients = []

def broadcast(message, _client=None):
    for client in clients:
        client_socket, _, _ = client
        if client_socket != _client:
            client_socket.send(message)

def update_client_list():
    client_list = "Clientes conectados:\n" + "\n".join([f"{name} ({ip})" for _, name, ip in clients])
    client_list_message = client_list.encode('utf-8')
    broadcast(client_list_message)

def handle_client(client_socket, address):
    try:
        name = client_socket.recv(1024).decode('utf-8')
        clients.append((client_socket, name, address[0]))
        print(f"{name} ({address[0]}) se conectou.")
        
        welcome_message = f"{name} entrou no chat.".encode('utf-8')
        broadcast(welcome_message)
        update_client_list()
        
        while True:
            message = client_socket.recv(1024)
            if not message:
                break
            broadcast(f"{name}: {message.decode('utf-8')}".encode('utf-8'))
    except:
        pass
    finally:
        client_socket.close()
        clients.remove((client_socket, name, address[0]))
        exit_message = f"{name} saiu do chat.".encode('utf-8')
        broadcast(exit_message)
        update_client_list()
        print(f"{name} ({address[0]}) desconectou.")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Servidor está ouvindo em {HOST}:{PORT}...")
    
    while True:
        client_socket, address = server.accept()
        threading.Thread(target=handle_client, args=(client_socket, address)).start()

if __name__ == "__main__":
    start_server()
