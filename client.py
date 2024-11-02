import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, ttk

HOST = '127.0.0.1'
PORT = 12345

class ChatClient:
    def __init__(self, host, port):
        self.root = tk.Tk()
        self.root.withdraw()
        self.name = simpledialog.askstring("Nome", "Digite seu nome:", parent=self.root)
        
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.client_socket.send(self.name.encode('utf-8'))
        
        self.root.deiconify()
        self.root.title("Chat")
        
        self.chat_area = scrolledtext.ScrolledText(self.root)
        self.chat_area.pack(padx=20, pady=5)
        self.chat_area.config(state='disabled')

        self.message_entry = tk.Entry(self.root)
        self.message_entry.pack(padx=20, pady=5)
        self.message_entry.bind("<Return>", self.send_message)

        self.user_dropdown = ttk.Combobox(self.root, values=["Todos"])
        self.user_dropdown.pack(pady=5)
        self.user_dropdown.current(0)  # Seleciona "Todos" por padrão

        self.disconnect_button = tk.Button(self.root, text="Desconectar", command=self.on_closing)
        self.disconnect_button.pack(pady=5)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Flag para controlar a execução do loop de recebimento de mensagens
        self.running = True
        threading.Thread(target=self.receive_messages).start()

    def send_message(self, event=None):
        """Envia uma mensagem para o servidor, com suporte a unicast."""
        message = self.message_entry.get()
        self.message_entry.delete(0, tk.END)
        
        # Determina o destinatário
        recipient = self.user_dropdown.get()
        if recipient == "Todos":
            self.client_socket.send(f"ALL:{message}".encode('utf-8'))
        elif recipient != "(você)":
            # Envia para o destinatário escolhido, exceto "(você)"
            self.client_socket.send(f"UNICAST:{recipient}:{message}".encode('utf-8'))

    def receive_messages(self):
        """Recebe mensagens do servidor e atualiza a lista de usuários."""
        while self.running:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message.startswith("USERS:"):
                    # Atualiza a lista de usuários conectados
                    users = message[6:].split(",")
                    
                    # Substitui o nome do usuário por "(você)" se for o próprio
                    users = ["Todos"] + ["(você)" if user == self.name else user for user in users]
                    self.user_dropdown["values"] = users
                else:
                    # Exibe a mensagem recebida no chat
                    self.chat_area.config(state='normal')
                    self.chat_area.insert(tk.END, message + "\n")
                    self.chat_area.config(state='disabled')
                    self.chat_area.yview(tk.END)
            except:
                break

    def on_closing(self):
        """Fecha o cliente de forma segura."""
        self.running = False  # Para o loop de recebimento de mensagens
        try:
            # Envia uma mensagem de desconexão e fecha o socket
            self.client_socket.send(f"DISCONNECT:{self.name}".encode('utf-8'))
            self.client_socket.shutdown(socket.SHUT_RDWR)
            self.client_socket.close()
        except:
            pass
        self.root.quit()

if __name__ == "__main__":
    ChatClient(HOST, PORT).root.mainloop()
