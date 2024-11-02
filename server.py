import socket
import threading

HOST = '127.0.0.1'
PORT = 12345

clients = []

def broadcast(message, _client=None):
    """Envia uma mensagem para todos os clientes, exceto o especificado."""
    for client_socket, _, _ in clients:
        if client_socket != _client:
            client_socket.send(message)

def send_unicast(sender, recipient, message):
    """Envia uma mensagem privada (unicast) para um destinatário específico."""
    for client_socket, name, _ in clients:
        if name == recipient:
            client_socket.send(f"[Privado de {sender}]: {message}".encode('utf-8'))
            break

def update_client_list():
    """Envia a lista atualizada de usuários para todos os clientes."""
    user_list = ",".join([name for _, name, _ in clients])
    broadcast(f"USERS:{user_list}".encode('utf-8'))

def handle_client(client_socket, address):
    """Lida com cada cliente que se conecta ao servidor."""
    try:
        # Recebe o nome do cliente
        name = client_socket.recv(1024).decode('utf-8')
        
        # Pergunta ao operador do servidor se deseja aceitar a conexão
        print(f"Nova solicitação de conexão de {name} ({address[0]})")
        accept = input(f"Aceitar conexão de {name} ({address[0]})? (/s para aceitar, /n para recusar): ").strip().lower()

        if accept != '/s':
            # Recusa a conexão
            print(f"Conexão de {name} ({address[0]}) recusada.")
            client_socket.send("Sua conexão foi recusada pelo servidor.".encode('utf-8'))
            client_socket.close()
            return
        
        clients.append((client_socket, name, address[0]))
        update_client_list()

        broadcast(f"{name} entrou no chat.".encode('utf-8'))
        
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            
            if message.startswith("ALL:"):
                # Mensagem para todos os clientes
                broadcast(f"{name}: {message[4:]}".encode('utf-8'))
            elif message.startswith("UNICAST:"):
                # Mensagem unicast para um destinatário específico
                _, recipient, unicast_message = message.split(":", 2)
                send_unicast(name, recipient, unicast_message)
            elif message.startswith("DISCONNECT:"):
                # Tratamento para quando um cliente se desconectar
                break
    except:
        pass
    finally:
        # Remove o cliente e atualiza a lista
        client_socket.close()
        clients.remove((client_socket, name, address[0]))
        update_client_list()
        broadcast(f"{name} saiu do chat.".encode('utf-8'))

def start_server():
    """Inicia o servidor e aguarda conexões dos clientes."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Servidor está ouvindo em {HOST}:{PORT}...")
    
    while True:
        client_socket, address = server.accept()
        threading.Thread(target=handle_client, args=(client_socket, address)).start()

if __name__ == "__main__":
    start_server()
