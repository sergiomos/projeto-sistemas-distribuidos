# 🚀 Quick Start Guide

Guia rápido para colocar o sistema funcionando em 5 minutos.

## ⚡ Início Rápido (TL;DR)

```bash
cd src
docker-compose up --build -d
docker-compose run --rm client node main.js
```

Pronto! O sistema está rodando.

## 📋 Pré-requisitos

- Docker instalado
- Docker Compose instalado
- 2GB de RAM disponível
- Portas 5555-5559 livres

## 🎯 Passo a Passo

### 1️⃣ Iniciar o Sistema (2 minutos)

```bash
# Navegue até o diretório
cd /home/sergiomos/dev/projeto-sistemas-distribuidos/src

# Inicie todos os containers
docker-compose up --build -d
```

Aguarde a mensagem: `✔ Container reference  Started`

### 2️⃣ Verificar Status (30 segundos)

```bash
# Ver containers rodando
docker-compose ps
```

Você deve ver:
- ✅ broker (1 container)
- ✅ proxy (1 container)
- ✅ reference (1 container)
- ✅ server (3 containers)
- ✅ bot (2 containers)

### 3️⃣ Conectar Cliente (1 minuto)

```bash
# Conectar ao cliente
docker-compose run --rm client node main.js
```

Digite seu nome quando solicitado: `usuario1`

### 4️⃣ Testar Funcionalidades (2 minutos)

#### Criar Canal
```
Escolha opção: 2
Nome do canal: geral
✅ Canal criado: geral
```

#### Listar Canais
```
Escolha opção: 3
✅ Canais disponíveis: ['geral']
```

#### Inscrever no Canal
```
Escolha opção: 4
Canal para se inscrever: geral
✅ Inscrito no canal: geral
```

#### Publicar Mensagem
```
Escolha opção: 5
Canal: geral
Mensagem: Olá mundo!
✅ Mensagem publicada no canal geral
```

Você verá sua mensagem aparecer!

### 5️⃣ Ver Logs (Opcional)

Em outro terminal:

```bash
cd src

# Ver logs em tempo real
docker-compose logs -f

# Ver apenas servidores
docker-compose logs -f server

# Ver apenas bots
docker-compose logs -f bot
```

## 🎉 Pronto!

Agora você tem:
- ✅ Sistema distribuído rodando
- ✅ 3 servidores replicando dados
- ✅ 2 bots gerando mensagens
- ✅ Cliente conectado
- ✅ Canal criado
- ✅ Mensagens sendo trocadas

## 🧪 Testes Rápidos

### Teste 1: Ver Bots em Ação
```bash
docker-compose logs -f bot
```
Você verá bots publicando mensagens automaticamente.

### Teste 2: Ver Replicação
```bash
docker-compose logs server | grep -i replic
```
Você verá servidores replicando dados entre si.

### Teste 3: Segundo Cliente
Em outro terminal:
```bash
docker-compose run --rm client node main.js
```
Faça login como `usuario2` e teste enviar mensagem para `usuario1`.

### Teste 4: Escalabilidade
```bash
# Adicionar mais bots
docker-compose up -d --scale bot=5

# Ver atividade aumentar
docker-compose logs -f bot
```

## 🛑 Parar o Sistema

```bash
# Parar tudo
docker-compose down

# Parar e remover dados
docker-compose down -v
```

## 📚 Próximos Passos

Agora que o sistema está rodando, explore:

1. **[README.md](README.md)** - Documentação completa
2. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Como funciona
3. **[TESTING.md](TESTING.md)** - Testes detalhados
4. **[COMMANDS.md](COMMANDS.md)** - Comandos úteis

## ❓ Problemas Comuns

### Porta em Uso
```bash
# Verificar portas
sudo lsof -i :5555
sudo lsof -i :5556

# Matar processo usando a porta
sudo kill -9 <PID>
```

### Container Não Inicia
```bash
# Ver erro
docker-compose logs [service_name]

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

### Cliente Não Conecta
```bash
# Reiniciar broker
docker-compose restart broker

# Verificar logs
docker-compose logs broker
```

### Limpar Tudo e Recomeçar
```bash
docker-compose down -v
docker system prune -af
cd src && docker-compose up --build -d
```

## 💡 Dicas

1. **Use múltiplos terminais**: Um para logs, outro para cliente
2. **Experimente com múltiplos clientes**: Cada um em um terminal
3. **Observe os relógios lógicos**: Veja os valores de Clock aumentando
4. **Teste escalabilidade**: Use `--scale` para adicionar mais containers
5. **Monitore recursos**: Use `docker stats` para ver uso de CPU/RAM

## 🎓 O Que Você Tem Agora

- **Broker** distribuindo requisições
- **Proxy** gerenciando pub/sub
- **3 Servidores** processando e replicando dados
- **2 Bots** gerando tráfego automático
- **Cliente** interativo para você usar
- **Relógios lógicos** ordenando eventos
- **Persistência** de todos os dados
- **Replicação** automática entre servidores

Tudo implementado com:
- ✅ Python
- ✅ JavaScript (Node.js)
- ✅ Go
- ✅ ZeroMQ
- ✅ MessagePack
- ✅ Docker

---

**Divirta-se explorando o sistema! 🚀**

