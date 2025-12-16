#!/usr/bin/env python3
import zmq
import json
import msgpack
import os
import time
import threading
import random
from datetime import datetime

# Diretório para persistência
DATA_DIR = "/app/data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
CHANNELS_FILE = os.path.join(DATA_DIR, "channels.json")
MESSAGES_FILE = os.path.join(DATA_DIR, "messages.json")
PUBLICATIONS_FILE = os.path.join(DATA_DIR, "publications.json")

class Server:
    def __init__(self, server_name=None):
        self.logical_clock = 0
        self.message_count = 0
        self.coordinator = None
        self.rank = None
        self.server_name = server_name or f"server_{random.randint(1000, 9999)}"
        self.servers_list = []
        
        self.users = {}
        self.channels = []
        
    def update_clock(self, received_clock=0):
        """Atualiza relógio lógico"""
        self.logical_clock = max(self.logical_clock, received_clock) + 1
        
    def increment_clock(self):
        """Incrementa relógio antes de enviar mensagem"""
        self.logical_clock += 1
        
    def ensure_data_dir(self):
        """Cria diretório de dados se não existir"""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

    def load_users(self):
        """Carrega usuários do disco"""
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, 'r') as f:
                    content = f.read()
                    if content.strip():
                        return json.loads(content)
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Aviso: Arquivo de usuários corrompido, reiniciando: {e}")
        return {}

    def save_users(self):
        """Salva usuários no disco"""
        with open(USERS_FILE, 'w') as f:
            json.dump(self.users, f, indent=2)

    def load_channels(self):
        """Carrega canais do disco"""
        if os.path.exists(CHANNELS_FILE):
            try:
                with open(CHANNELS_FILE, 'r') as f:
                    content = f.read()
                    if content.strip():
                        return json.loads(content)
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Aviso: Arquivo de canais corrompido, reiniciando: {e}")
        return []

    def save_channels(self):
        """Salva canais no disco"""
        with open(CHANNELS_FILE, 'w') as f:
            json.dump(self.channels, f, indent=2)

    def save_message(self, message_data):
        """Salva mensagem no disco"""
        messages = []
        if os.path.exists(MESSAGES_FILE):
            try:
                with open(MESSAGES_FILE, 'r') as f:
                    content = f.read()
                    if content.strip():  # Verifica se não está vazio
                        messages = json.loads(content)
            except (json.JSONDecodeError, ValueError) as e:
                print(f"[{self.server_name}] Aviso: Arquivo de mensagens corrompido, reiniciando: {e}")
                messages = []
        messages.append(message_data)
        with open(MESSAGES_FILE, 'w') as f:
            json.dump(messages, f, indent=2)

    def save_publication(self, publication_data):
        """Salva publicação no disco"""
        publications = []
        if os.path.exists(PUBLICATIONS_FILE):
            try:
                with open(PUBLICATIONS_FILE, 'r') as f:
                    content = f.read()
                    if content.strip():  # Verifica se não está vazio
                        publications = json.loads(content)
            except (json.JSONDecodeError, ValueError) as e:
                print(f"[{self.server_name}] Aviso: Arquivo de publicações corrompido, reiniciando: {e}")
                publications = []
        publications.append(publication_data)
        with open(PUBLICATIONS_FILE, 'w') as f:
            json.dump(publications, f, indent=2)

    def register_with_reference(self, ref_socket):
        """Registra servidor e obtém rank"""
        try:
            self.increment_clock()
            message = {
                "service": "rank",
                "data": {
                    "user": self.server_name,
                    "timestamp": datetime.now().isoformat(),
                    "clock": self.logical_clock
                }
            }
            ref_socket.send(msgpack.packb(message))
            response_bytes = ref_socket.recv()
            response = msgpack.unpackb(response_bytes, raw=False)
            
            self.update_clock(response["data"].get("clock", 0))
            self.rank = response["data"]["rank"]
            print(f"[{self.server_name}] Rank recebido: {self.rank}, Clock: {self.logical_clock}")
        except Exception as e:
            print(f"Erro ao registrar no servidor de referência: {e}")
            self.rank = random.randint(1, 1000)

    def get_servers_list(self, ref_socket):
        """Obtém lista de servidores do servidor de referência"""
        try:
            self.increment_clock()
            message = {
                "service": "list",
                "data": {
                    "timestamp": datetime.now().isoformat(),
                    "clock": self.logical_clock
                }
            }
            ref_socket.send(msgpack.packb(message))
            response_bytes = ref_socket.recv()
            response = msgpack.unpackb(response_bytes, raw=False)
            
            self.update_clock(response["data"].get("clock", 0))
            self.servers_list = response["data"]["list"]
            print(f"[{self.server_name}] Servidores ativos: {len(self.servers_list)}")
        except Exception as e:
            print(f"Erro ao obter lista de servidores: {e}")

    def send_heartbeat(self, ref_socket):
        """Envia heartbeat periódico ao servidor de referência"""
        while True:
            try:
                time.sleep(10)
                self.increment_clock()
                message = {
                    "service": "heartbeat",
                    "data": {
                        "user": self.server_name,
                        "timestamp": datetime.now().isoformat(),
                        "clock": self.logical_clock
                    }
                }
                ref_socket.send(msgpack.packb(message))
                response_bytes = ref_socket.recv()
                response = msgpack.unpackb(response_bytes, raw=False)
                self.update_clock(response["data"].get("clock", 0))
            except Exception as e:
                print(f"Erro ao enviar heartbeat: {e}")

    def replicate_data(self, pub_socket, operation, data):
        """Replica dados para outros servidores"""
        self.increment_clock()
        replication_msg = {
            "operation": operation,
            "data": data,
            "server": self.server_name,
            "clock": self.logical_clock
        }
        packed = msgpack.packb(replication_msg)
        pub_socket.send_multipart([b"replication", packed])
        print(f"[{self.server_name}] Replicando: {operation}")
    
    def handle_replication(self, replication_data):
        """Processa dados replicados de outros servidores"""
        operation = replication_data.get("operation")
        data = replication_data.get("data")
        source_server = replication_data.get("server")
        
        # Não processa replicação do próprio servidor
        if source_server == self.server_name:
            return
        
        print(f"[{self.server_name}] Recebendo replicação de {source_server}: {operation}")
        
        if operation == "login":
            user = data.get("user")
            timestamp = data.get("timestamp")
            if user not in self.users:
                self.users[user] = []
            if timestamp not in self.users[user]:
                self.users[user].append(timestamp)
                self.save_users()
                
        elif operation == "channel":
            channel = data.get("channel")
            if channel and channel not in self.channels:
                self.channels.append(channel)
                self.save_channels()
                
        elif operation == "message":
            self.save_message(data)
            
        elif operation == "publication":
            self.save_publication(data)

    def handle_login(self, data, pub_socket=None):
        """Processa login de usuário"""
        self.update_clock(data.get("clock", 0))
        
        user = data.get("user")
        timestamp = data.get("timestamp")
        
        if not user:
            self.increment_clock()
            return {
                "service": "login",
                "data": {
                    "status": "erro",
                    "timestamp": datetime.now().isoformat(),
                    "clock": self.logical_clock,
                    "description": "Nome de usuário não fornecido"
                }
            }
        
        if user not in self.users:
            self.users[user] = []
        
        self.users[user].append(timestamp)
        self.save_users()
        
        # Replica para outros servidores
        if pub_socket:
            self.replicate_data(pub_socket, "login", {"user": user, "timestamp": timestamp})
        
        self.increment_clock()
        return {
            "service": "login",
            "data": {
                "status": "sucesso",
                "timestamp": datetime.now().isoformat(),
                "clock": self.logical_clock
            }
        }

    def handle_users(self, data):
        """Retorna lista de usuários"""
        self.update_clock(data.get("clock", 0))
        self.increment_clock()
        
        return {
            "service": "users",
            "data": {
                "timestamp": datetime.now().isoformat(),
                "clock": self.logical_clock,
                "users": list(self.users.keys())
            }
        }

    def handle_channel(self, data, pub_socket=None):
        """Cria um novo canal"""
        self.update_clock(data.get("clock", 0))
        
        channel = data.get("channel")
        
        if not channel:
            self.increment_clock()
            return {
                "service": "channel",
                "data": {
                    "status": "erro",
                    "timestamp": datetime.now().isoformat(),
                    "clock": self.logical_clock,
                    "description": "Nome de canal não fornecido"
                }
            }
        
        if channel in self.channels:
            self.increment_clock()
            return {
                "service": "channel",
                "data": {
                    "status": "erro",
                    "timestamp": datetime.now().isoformat(),
                    "clock": self.logical_clock,
                    "description": "Canal já existe"
                }
            }
        
        self.channels.append(channel)
        self.save_channels()
        
        # Replica para outros servidores
        if pub_socket:
            self.replicate_data(pub_socket, "channel", {"channel": channel})
        
        self.increment_clock()
        return {
            "service": "channel",
            "data": {
                "status": "sucesso",
                "timestamp": datetime.now().isoformat(),
                "clock": self.logical_clock
            }
        }

    def handle_channels(self, data):
        """Retorna lista de canais"""
        self.update_clock(data.get("clock", 0))
        self.increment_clock()
        
        return {
            "service": "channels",
            "data": {
                "timestamp": datetime.now().isoformat(),
                "clock": self.logical_clock,
                "channels": self.channels
            }
        }

    def handle_publish(self, data, pub_socket):
        """Publica mensagem em um canal"""
        self.update_clock(data.get("clock", 0))
        
        user = data.get("user")
        channel = data.get("channel")
        message = data.get("message")
        timestamp = data.get("timestamp")
        
        if channel not in self.channels:
            self.increment_clock()
            return {
                "service": "publish",
                "data": {
                    "status": "erro",
                    "message": "Canal não existe",
                    "timestamp": datetime.now().isoformat(),
                    "clock": self.logical_clock
                }
            }
        
        # Publica no canal
        self.increment_clock()
        publication = {
            "user": user,
            "message": message,
            "timestamp": timestamp,
            "clock": self.logical_clock
        }
        
        pub_message = msgpack.packb(publication)
        pub_socket.send_multipart([channel.encode(), pub_message])
        
        # Salva publicação
        pub_data = {
            "channel": channel,
            "user": user,
            "message": message,
            "timestamp": timestamp,
            "clock": self.logical_clock
        }
        self.save_publication(pub_data)
        
        # Replica para outros servidores
        self.replicate_data(pub_socket, "publication", pub_data)
        
        self.message_count += 1
        
        return {
            "service": "publish",
            "data": {
                "status": "OK",
                "timestamp": datetime.now().isoformat(),
                "clock": self.logical_clock
            }
        }

    def handle_message(self, data, pub_socket):
        """Envia mensagem privada para usuário"""
        self.update_clock(data.get("clock", 0))
        
        src = data.get("src")
        dst = data.get("dst")
        message = data.get("message")
        timestamp = data.get("timestamp")
        
        if dst not in self.users:
            self.increment_clock()
            return {
                "service": "message",
                "data": {
                    "status": "erro",
                    "message": "Usuário não existe",
                    "timestamp": datetime.now().isoformat(),
                    "clock": self.logical_clock
                }
            }
        
        # Publica no tópico do usuário
        self.increment_clock()
        private_message = {
            "src": src,
            "message": message,
            "timestamp": timestamp,
            "clock": self.logical_clock
        }
        
        pub_message = msgpack.packb(private_message)
        pub_socket.send_multipart([dst.encode(), pub_message])
        
        # Salva mensagem
        msg_data = {
            "src": src,
            "dst": dst,
            "message": message,
            "timestamp": timestamp,
            "clock": self.logical_clock
        }
        self.save_message(msg_data)
        
        # Replica para outros servidores
        self.replicate_data(pub_socket, "message", msg_data)
        
        self.message_count += 1
        
        return {
            "service": "message",
            "data": {
                "status": "OK",
                "timestamp": datetime.now().isoformat(),
                "clock": self.logical_clock
            }
        }

    def run(self):
        self.ensure_data_dir()
        self.users = self.load_users()
        self.channels = self.load_channels()
        
        context = zmq.Context()
        
        # Socket REP para requisições do broker
        rep_socket = context.socket(zmq.REP)
        rep_socket.connect("tcp://broker:5556")
        
        # Socket PUB para publicações no proxy
        pub_socket = context.socket(zmq.PUB)
        pub_socket.connect("tcp://proxy:5557")
        
        # Socket SUB para receber coordenador e replicação
        sub_socket = context.socket(zmq.SUB)
        sub_socket.connect("tcp://proxy:5558")
        sub_socket.subscribe("servers")
        sub_socket.subscribe("replication")
        
        # Socket REQ para comunicação com servidor de referência
        ref_socket = context.socket(zmq.REQ)
        ref_socket.connect("tcp://reference:5559")
        
        # Registra no servidor de referência
        self.register_with_reference(ref_socket)
        self.get_servers_list(ref_socket)
        
        # Inicia thread de heartbeat
        heartbeat_thread = threading.Thread(target=self.send_heartbeat, args=(ref_socket,), daemon=True)
        heartbeat_thread.start()
        
        print(f"Servidor {self.server_name} (rank={self.rank}) iniciado, Clock: {self.logical_clock}")
        
        # Poller para múltiplos sockets
        poller = zmq.Poller()
        poller.register(rep_socket, zmq.POLLIN)
        poller.register(sub_socket, zmq.POLLIN)
        
        while True:
            try:
                socks = dict(poller.poll(timeout=1000))
                
                # Processa requisições dos clientes
                if rep_socket in socks:
                    message_bytes = rep_socket.recv()
                    message = msgpack.unpackb(message_bytes, raw=False)
                    
                    service = message.get("service")
                    data = message.get("data", {})
                    
                    print(f"[{self.server_name} Clock={self.logical_clock}] Recebido: {service}")
                    
                    if service == "login":
                        response = self.handle_login(data, pub_socket)
                    elif service == "users":
                        response = self.handle_users(data)
                    elif service == "channel":
                        response = self.handle_channel(data, pub_socket)
                    elif service == "channels":
                        response = self.handle_channels(data)
                    elif service == "publish":
                        response = self.handle_publish(data, pub_socket)
                    elif service == "message":
                        response = self.handle_message(data, pub_socket)
                    else:
                        self.increment_clock()
                        response = {
                            "service": service,
                            "data": {
                                "status": "erro",
                                "timestamp": datetime.now().isoformat(),
                                "clock": self.logical_clock,
                                "description": f"Serviço desconhecido: {service}"
                            }
                        }
                    
                    response_bytes = msgpack.packb(response)
                    rep_socket.send(response_bytes)
                
                # Recebe notificação de novo coordenador ou replicação
                if sub_socket in socks:
                    topic, msg = sub_socket.recv_multipart()
                    topic_str = topic.decode()
                    data = msgpack.unpackb(msg, raw=False)
                    self.update_clock(data.get("clock", 0))
                    
                    if topic_str == "servers":
                        self.coordinator = data.get("coordinator")
                        coordinator_rank = data.get("rank", "?")
                        is_coordinator = (self.coordinator == self.server_name)
                        status = "EU SOU O COORDENADOR!" if is_coordinator else f"Coordenador é {self.coordinator}"
                        print(f"[{self.server_name}] ⚡ ELEIÇÃO: {status} (rank={coordinator_rank}, Clock={self.logical_clock})")
                    elif topic_str == "replication":
                        self.handle_replication(data)
                    
            except Exception as e:
                print(f"Erro: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    import sys
    server_name = sys.argv[1] if len(sys.argv) > 1 else None
    server = Server(server_name)
    server.run()
