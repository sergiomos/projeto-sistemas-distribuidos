#!/usr/bin/env python3
import zmq
import msgpack
import time
from datetime import datetime

class ReferenceServer:
    def __init__(self):
        self.servers = {}  # {name: {"rank": int, "last_heartbeat": timestamp}}
        self.next_rank = 0
        self.logical_clock = 0
        
    def update_clock(self, received_clock):
        """Atualiza relógio lógico"""
        self.logical_clock = max(self.logical_clock, received_clock) + 1
        
    def handle_rank(self, data):
        """Fornece rank para servidor"""
        self.update_clock(data.get("clock", 0))
        
        server_name = data.get("user")
        
        if server_name not in self.servers:
            # Novo servidor
            rank = self.next_rank
            self.next_rank += 1
            self.servers[server_name] = {
                "rank": rank,
                "last_heartbeat": time.time()
            }
        else:
            rank = self.servers[server_name]["rank"]
        
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
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:5559")
        
        print("Servidor de referência iniciado na porta 5559")
        
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

