#!/usr/bin/env python3
import zmq

def main():
    context = zmq.Context()
    
    # Socket para clientes (ROUTER)
    client_socket = context.socket(zmq.ROUTER)
    client_socket.bind("tcp://*:5555")
    
    # Socket para servidores (DEALER) - balanceamento round-robin
    server_socket = context.socket(zmq.DEALER)
    server_socket.bind("tcp://*:5556")
    
    print("Broker iniciado - Balanceamento de carga entre clientes e servidores")
    
    # Proxy para balanceamento automático
    zmq.proxy(client_socket, server_socket)

if __name__ == "__main__":
    main()
