#!/bin/bash

echo "==================================="
echo "Sistema de Mensagens Distribuído"
echo "==================================="
echo ""

case "$1" in
  start)
    echo "Iniciando sistema..."
    docker-compose up -d
    echo "Sistema iniciado!"
    echo "Use './scripts/init.sh logs' para ver os logs"
    echo "Use './scripts/init.sh client' para conectar um cliente"
    ;;
    
  stop)
    echo "Parando sistema..."
    docker-compose down
    echo "Sistema parado!"
    ;;
    
  restart)
    echo "Reiniciando sistema..."
    docker-compose restart
    echo "Sistema reiniciado!"
    ;;
    
  build)
    echo "Reconstruindo containers..."
    docker-compose up -d --build
    echo "Containers reconstruídos!"
    ;;
    
  logs)
    docker-compose logs -f
    ;;
    
  client)
    echo "Conectando cliente..."
    docker-compose run --rm client node main.js
    ;;
    
  clean)
    echo "Limpando sistema (ATENÇÃO: Remove todos os dados!)..."
    read -p "Tem certeza? (s/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
      docker-compose down -v
      docker system prune -f
      echo "Sistema limpo!"
    else
      echo "Operação cancelada."
    fi
    ;;
    
  status)
    echo "Status dos containers:"
    docker-compose ps
    ;;
    
  scale-servers)
    echo "Escalando servidores para $2 réplicas..."
    docker-compose up -d --scale server=$2
    ;;
    
  scale-bots)
    echo "Escalando bots para $2 réplicas..."
    docker-compose up -d --scale bot=$2
    ;;
    
  *)
    echo "Uso: $0 {start|stop|restart|build|logs|client|clean|status|scale-servers N|scale-bots N}"
    echo ""
    echo "Comandos:"
    echo "  start           - Inicia o sistema"
    echo "  stop            - Para o sistema"
    echo "  restart         - Reinicia o sistema"
    echo "  build           - Reconstrói e inicia containers"
    echo "  logs            - Mostra logs em tempo real"
    echo "  client          - Conecta um cliente interativo"
    echo "  clean           - Remove todos os containers e dados"
    echo "  status          - Mostra status dos containers"
    echo "  scale-servers N - Escala servidores para N réplicas"
    echo "  scale-bots N    - Escala bots para N réplicas"
    exit 1
    ;;
esac

