import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog

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

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        threading.Thread(target=self.receive_messages).start()

    def send_message(self, event=None):
        """Envia mensagem para o servidor"""
        message = self.message_entry.get()
        self.message_entry.delete(0, tk.END)
        self.client_socket.send(message.encode('utf-8'))

    def receive_messages(self):
        """Recebe mensagens do servidor"""
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                self.chat_area.config(state='normal')
                self.chat_area.insert(tk.END, message + "\n")
                self.chat_area.config(state='disabled')
                self.chat_area.yview(tk.END)
            except:
                break

    def on_closing(self):
        """Fecha o cliente de forma segura"""
        self.client_socket.send("Saiu do chat".encode('utf-8'))
        self.client_socket.close()
        self.root.quit()

if __name__ == "__main__":
    ChatClient(HOST, PORT).root.mainloop()