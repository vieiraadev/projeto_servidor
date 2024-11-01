import socket
import threading

HOST = '0.0.0.0'  
PORT = 12345

clients = []

def broadcast(message, _client=None):
    """Envia mensagem a todos os clientes conectados"""
    for client in clients:
        client_socket, _ = client
        if client_socket != _client:
            client_socket.send(message)

def handle_client(client_socket, address):
    """Lida com a comunicação entre servidor e cliente"""
    try:
        # Recebe o nome do cliente
        name = client_socket.recv(1024).decode('utf-8')
        welcome_message = f"{name} entrou no chat.".encode('utf-8')
        broadcast(welcome_message)
        clients.append((client_socket, name))
        print(f"{name} ({address[0]}) se conectou.")
        
        while True:
            message = client_socket.recv(1024)
            if not message:
                break
            # Envia a mensagem para todos incluindo o remetente
            broadcast(f"{name}: {message.decode('utf-8')}".encode('utf-8'))
    except:
        pass
    finally:
        client_socket.close()
        clients.remove((client_socket, name))
        exit_message = f"{name} saiu do chat.".encode('utf-8')
        broadcast(exit_message)
        print(f"{name} ({address[0]}) desconectou.")

def start_server():
    """Inicia o servidor"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Servidor está ouvindo em {HOST}:{PORT}...")

    while True:
        client_socket, address = server.accept()
        threading.Thread(target=handle_client, args=(client_socket, address)).start()

if __name__ == "__main__":
    start_server()
