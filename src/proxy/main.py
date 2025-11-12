#!/usr/bin/env python3
import zmq

def main():
    context = zmq.Context()
    
    # XSUB para publishers
    xsub = context.socket(zmq.XSUB)
    xsub.bind("tcp://*:5557")
    
    # XPUB para subscribers
    xpub = context.socket(zmq.XPUB)
    xpub.bind("tcp://*:5558")
    
    print("Proxy Pub/Sub iniciado")
    
    # Proxy para pub/sub
    zmq.proxy(xsub, xpub)

if __name__ == "__main__":
    main()
