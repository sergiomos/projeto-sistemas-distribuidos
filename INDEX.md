# Índice da Documentação

## 📚 Documentação Principal

### [README.md](README.md)
Documentação completa do projeto incluindo:
- Descrição e arquitetura do sistema
- Funcionalidades implementadas
- Explicação detalhada da replicação de dados
- Instruções de execução
- Testes e simulação de falhas
- Resolução de problemas

### [QUICKSTART.md](QUICKSTART.md)
Guia rápido para começar em 5 minutos:
- Passos simplificados de instalação
- Exemplo de uso básico
- Comandos essenciais
- Exemplo de sessão completa

## 📁 Estrutura do Projeto

```
projeto-sistemas-distribuidos/
├── README.md                    # Documentação completa
├── QUICKSTART.md               # Guia rápido
├── INDEX.md                    # Este arquivo
└── src/                        # Código fonte
    ├── docker-compose.yml      # Orquestração dos serviços
    ├── Dockerfile.go           # Build do bot Go
    ├── Dockerfile.node         # Build do cliente Node.js
    ├── Dockerfile.python       # Build dos serviços Python
    ├── broker/                 # Broker de balanceamento
    │   └── main.py
    ├── proxy/                  # Proxy Pub/Sub
    │   └── main.py
    ├── reference/              # Servidor de referência
    │   └── main.py
    ├── server/                 # Servidores principais (3 réplicas)
    │   └── main.py
    ├── client/                 # Cliente interativo Node.js
    │   ├── main.js
    │   └── package.json
    └── bot/                    # Bot automático Go (2 réplicas)
        ├── main.go
        └── go.mod
```

## 🚀 Início Rápido

```bash
# 1. Clone o repositório
git clone <url-do-repositório>
cd projeto-sistemas-distribuidos

# 2. Inicie o sistema
cd src
docker compose up --build

# 3. Conecte ao cliente (em outro terminal)
docker exec -it src-client-1 node main.js
```

## 📖 Guias por Tópico

### Para Começar
1. [QUICKSTART.md](QUICKSTART.md) - Comece aqui!
2. [README.md - Arquitetura](README.md#arquitetura) - Entenda o sistema
3. [README.md - Como Executar](README.md#como-executar) - Instruções detalhadas

### Para Testar
1. [README.md - Referência Rápida](README.md#referência-rápida-de-comandos) - Comandos úteis
2. [README.md - Testar Funcionalidades](README.md#como-testar-as-funcionalidades) - Testes passo a passo
3. [README.md - Simulando Falhas](README.md#simulando-falhas-e-eleição-de-coordenador) - Testes avançados

### Para Entender
1. [README.md - Funcionalidades](README.md#funcionalidades-implementadas) - O que foi implementado
2. [README.md - Replicação](README.md#implementação-da-replicação-parte-5) - Como funciona a replicação
3. [README.md - Estrutura de Dados](README.md#estrutura-de-dados) - Formato das mensagens

### Para Resolver Problemas
1. [README.md - Resolução de Problemas](README.md#resolução-de-problemas) - Problemas comuns
2. [README.md - Ver Estado do Sistema](README.md#ver-estado-do-sistema-em-tempo-real) - Monitoramento

## 🎯 Casos de Uso Comuns

### Quero testar o sistema rapidamente
→ Siga o [QUICKSTART.md](QUICKSTART.md)

### Quero entender como funciona a replicação
→ Veja [README.md - Implementação da Replicação](README.md#implementação-da-replicação-parte-5)

### Quero simular falha de um servidor
→ Veja [README.md - Simulando Falhas](README.md#simulando-falhas-e-eleição-de-coordenador)

### Quero ver os dados persistidos
→ Use `docker exec src-server-1 cat /app/data/users.json`

### Estou tendo problemas
→ Veja [README.md - Resolução de Problemas](README.md#resolução-de-problemas)

### Quero contribuir ou modificar
→ Veja [README.md - Estrutura de Dados](README.md#estrutura-de-dados) e o código em `src/`

## 📝 Comandos Mais Usados

```bash
# Iniciar
cd src && docker compose up --build

# Ver logs
docker compose logs -f

# Conectar ao cliente
docker exec -it src-client-1 node main.js

# Ver dados
docker exec src-server-1 cat /app/data/channels.json

# Parar um servidor
docker stop src-server-1

# Reiniciar
docker restart src-server-1

# Limpar tudo
docker compose down --rmi all --volumes
```

## 🔗 Links Úteis

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [ZeroMQ Guide](https://zguide.zeromq.org/)
- [MessagePack](https://msgpack.org/)

## 💡 Dicas

- Use múltiplos terminais para ver logs enquanto testa
- Experimente parar e reiniciar servidores para ver a replicação
- Observe os relógios lógicos incrementando nas mensagens
- Crie múltiplos clientes para testar mensagens privadas
- Use `docker compose logs -f | grep "Clock="` para acompanhar sincronização

## 🎓 Conceitos de Sistemas Distribuídos Implementados

- ✅ Comunicação assíncrona (Pub/Sub)
- ✅ Comunicação síncrona (Request/Reply)
- ✅ Balanceamento de carga (ROUTER-DEALER)
- ✅ Replicação de dados
- ✅ Relógios lógicos
- ✅ Serialização binária (MessagePack)
- ✅ Persistência distribuída
- ✅ Detecção de falhas (Heartbeat)
- ✅ Sistema de ranks
- 🔄 Eleição de coordenador (infraestrutura pronta)
- 🔄 Sincronização de relógio (infraestrutura pronta)

---

**Legenda:**
- ✅ Totalmente implementado
- 🔄 Infraestrutura pronta, implementação parcial

