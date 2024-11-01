import socket
import threading

HOST = '0.0.0.0'  
PORT = 12345

clients = []

def broadcast(message, _client=None):
    """Envia mensagem a todos os clientes conectados"""
    for client in clients:
        if client != _client:
            client.send(message)

def handle_client(client, address):
    """Lida com a comunicação entre servidor e cliente"""
    print(f"{address} se conectou.")
    clients.append(client)
    broadcast(f"{address[0]} entrou no chat.".encode('utf-8'))

    while True:
        try:
            message = client.recv(1024)
            if not message:
                break
            broadcast(message, client)
        except:
            clients.remove(client)
            broadcast(f"{address[0]} saiu do chat.".encode('utf-8'))
            break

    client.close()

def start_server():
    """Inicia o servidor"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"Servidor está ouvindo em {HOST}:{PORT}...")

    while True:
        client, address = server.accept()
        threading.Thread(target=handle_client, args=(client, address)).start()

if __name__ == "__main__":
    start_server()
