#!/usr/bin/env python3
import zmq
import msgpack
import time
import threading
from datetime import datetime

class ReferenceServer:
    def __init__(self):
        self.servers = {}  # {name: {"rank": int, "last_heartbeat": timestamp}}
        self.next_rank = 0
        self.logical_clock = 0
        self.current_coordinator = None
        self.pub_socket = None
        
    def update_clock(self, received_clock):
        """Atualiza relógio lógico"""
        self.logical_clock = max(self.logical_clock, received_clock) + 1
    
    def get_coordinator(self):
        """Retorna o coordenador (servidor com menor rank ativo)"""
        current_time = time.time()
        active_servers = {
            name: info for name, info in self.servers.items()
            if current_time - info["last_heartbeat"] < 30
        }
        
        if not active_servers:
            return None
        
        # Coordenador é o servidor com menor rank
        coordinator = min(active_servers.items(), key=lambda x: x[1]["rank"])
        return coordinator[0]
    
    def publish_coordinator(self):
        """Publica o coordenador atual para todos os servidores"""
        if not self.pub_socket:
            return
        
        coordinator = self.get_coordinator()
        
        # Só publica se mudou
        if coordinator != self.current_coordinator:
            old_coordinator = self.current_coordinator
            self.current_coordinator = coordinator
            
            if coordinator:
                self.logical_clock += 1
                message = {
                    "coordinator": coordinator,
                    "rank": self.servers[coordinator]["rank"],
                    "clock": self.logical_clock
                }
                
                packed = msgpack.packb(message)
                self.pub_socket.send_multipart([b"servers", packed])
                
                if old_coordinator:
                    print(f"[ELEIÇÃO] Mudança de coordenador: {old_coordinator} -> {coordinator}")
                else:
                    print(f"[ELEIÇÃO] Coordenador inicial eleito: {coordinator} (rank={self.servers[coordinator]['rank']})")
    
    def monitor_coordinator(self):
        """Thread que monitora e publica mudanças de coordenador"""
        while True:
            try:
                time.sleep(5)  # Verifica a cada 5 segundos
                self.publish_coordinator()
            except Exception as e:
                print(f"Erro no monitor de coordenador: {e}")
        
    def handle_rank(self, data):
        """Fornece rank para servidor"""
        self.update_clock(data.get("clock", 0))
        
        server_name = data.get("user")
        is_new_server = server_name not in self.servers
        
        if is_new_server:
            # Novo servidor
            rank = self.next_rank
            self.next_rank += 1
            self.servers[server_name] = {
                "rank": rank,
                "last_heartbeat": time.time()
            }
            print(f"[REGISTRO] Novo servidor registrado: {server_name} (rank={rank})")
        else:
            rank = self.servers[server_name]["rank"]
            self.servers[server_name]["last_heartbeat"] = time.time()
        
        # Publica coordenador quando novo servidor entra
        if is_new_server:
            # Aguarda um pouco para garantir que o servidor está pronto
            threading.Timer(2.0, self.publish_coordinator).start()
        
        return {
            "service": "rank",
            "data": {
                "rank": rank,
                "timestamp": datetime.now().isoformat(),
                "clock": self.logical_clock
            }
        }
    
    def handle_list(self, data):
        """Retorna lista de servidores ativos"""
        self.update_clock(data.get("clock", 0))
        
        # Remove servidores inativos (sem heartbeat há mais de 30s)
        current_time = time.time()
        active_servers = {
            name: info for name, info in self.servers.items()
            if current_time - info["last_heartbeat"] < 30
        }
        
        server_list = [
            {"name": name, "rank": info["rank"]}
            for name, info in active_servers.items()
        ]
        
        return {
            "service": "list",
            "data": {
                "list": server_list,
                "timestamp": datetime.now().isoformat(),
                "clock": self.logical_clock
            }
        }
    
    def handle_heartbeat(self, data):
        """Atualiza heartbeat do servidor"""
        self.update_clock(data.get("clock", 0))
        
        server_name = data.get("user")
        
        if server_name in self.servers:
            self.servers[server_name]["last_heartbeat"] = time.time()
        
        return {
            "service": "heartbeat",
            "data": {
                "timestamp": datetime.now().isoformat(),
                "clock": self.logical_clock
            }
        }
    
    def run(self):
        context = zmq.Context()
        
        # Socket REP para requisições
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:5559")
        
        # Socket PUB para notificações de coordenador
        self.pub_socket = context.socket(zmq.PUB)
        self.pub_socket.connect("tcp://proxy:5557")
        
        # Aguarda um pouco para conexão estabelecer
        time.sleep(1)
        
        print("Servidor de referência iniciado na porta 5559")
        print("Conectado ao proxy para publicação de eleições")
        
        # Inicia thread de monitoramento de coordenador
        monitor_thread = threading.Thread(target=self.monitor_coordinator, daemon=True)
        monitor_thread.start()
        
        while True:
            try:
                message_bytes = socket.recv()
                message = msgpack.unpackb(message_bytes, raw=False)
                
                service = message.get("service")
                data = message.get("data", {})
                
                print(f"[Clock={self.logical_clock}] Recebido: {service}")
                
                if service == "rank":
                    response = self.handle_rank(data)
                elif service == "list":
                    response = self.handle_list(data)
                elif service == "heartbeat":
                    response = self.handle_heartbeat(data)
                else:
                    self.logical_clock += 1
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
                socket.send(response_bytes)
                print(f"[Clock={self.logical_clock}] Respondido: {service}")
                
            except Exception as e:
                print(f"Erro: {e}")

if __name__ == "__main__":
    server = ReferenceServer()
    server.run()

