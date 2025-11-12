# Comandos Úteis

Referência rápida de comandos para o projeto.

## 🚀 Inicialização

```bash
# Ir para o diretório
cd /home/sergiomos/dev/projeto-sistemas-distribuidos/src

# Build e iniciar tudo
docker-compose up --build

# Iniciar em background
docker-compose up -d --build

# Iniciar sem rebuild
docker-compose up -d
```

## 🔌 Conectar Cliente

```bash
# Cliente interativo
docker-compose exec client node main.js

# Criar novo cliente (não interfere com outros)
docker-compose run --rm client node main.js

# Cliente em novo container
docker-compose run --rm -it client node main.js
```

## 📊 Logs

```bash
# Ver todos os logs
docker-compose logs

# Logs em tempo real
docker-compose logs -f

# Logs de componente específico
docker-compose logs -f server
docker-compose logs -f broker
docker-compose logs -f proxy
docker-compose logs -f reference
docker-compose logs -f bot
docker-compose logs -f client

# Últimas N linhas
docker-compose logs --tail=50 server

# Filtrar logs
docker-compose logs server | grep Clock
docker-compose logs server | grep -i replicando
docker-compose logs bot | grep Publicou
```

## 🔍 Status

```bash
# Ver containers rodando
docker-compose ps

# Status detalhado
docker ps -a

# Ver recursos usados
docker stats

# Ver networks
docker network ls

# Ver volumes
docker volume ls
```

## 🔄 Controle de Containers

```bash
# Parar tudo
docker-compose down

# Parar mas manter volumes
docker-compose stop

# Reiniciar
docker-compose restart

# Reiniciar componente específico
docker-compose restart server
docker-compose restart broker

# Recriar containers
docker-compose up -d --force-recreate
```

## 📈 Escalabilidade

```bash
# Escalar servidores (padrão: 3)
docker-compose up -d --scale server=5

# Escalar bots (padrão: 2)
docker-compose up -d --scale bot=5

# Escalar ambos
docker-compose up -d --scale server=5 --scale bot=10

# Reduzir servidores
docker-compose up -d --scale server=1
```

## 🐛 Debug

```bash
# Entrar em container
docker-compose exec broker sh
docker-compose exec server sh
docker-compose exec client sh

# Executar comando em container
docker-compose exec server ls -la /app/data
docker-compose exec server cat /app/data/users.json

# Ver processos no container
docker-compose exec server ps aux

# Ver arquivos de dados
docker-compose exec server cat /app/data/users.json
docker-compose exec server cat /app/data/channels.json
docker-compose exec server cat /app/data/messages.json
docker-compose exec server cat /app/data/publications.json
```

## 🧹 Limpeza

```bash
# Parar e remover containers
docker-compose down

# Remover também volumes (PERDE DADOS!)
docker-compose down -v

# Limpar imagens não usadas
docker image prune

# Limpar tudo (CUIDADO!)
docker system prune -a

# Remover apenas containers parados
docker container prune

# Remover volumes não usados
docker volume prune
```

## 📦 Build

```bash
# Rebuild tudo
docker-compose build

# Rebuild sem cache
docker-compose build --no-cache

# Rebuild componente específico
docker-compose build server
docker-compose build client
docker-compose build bot

# Rebuild e iniciar
docker-compose up -d --build
```

## 🔧 Desenvolvimento

```bash
# Ver mudanças em tempo real (logs)
docker-compose logs -f server

# Reiniciar após mudança de código
docker-compose restart server

# Rebuild após mudança
docker-compose up -d --build server

# Parar, rebuild, iniciar
docker-compose down && docker-compose up --build
```

## 📈 Monitoramento

```bash
# CPU e Memória em tempo real
docker stats

# Específico de um container
docker stats broker

# Uso de disco
docker system df

# Containers em execução
watch docker-compose ps

# Logs contínuos de múltiplos serviços
docker-compose logs -f broker proxy server
```

## 🧪 Testes

```bash
# Testar broker
docker-compose logs broker | grep iniciado

# Testar servidores
docker-compose logs server | grep Rank

# Testar replicação
docker-compose logs server | grep -i replic

# Testar bots
docker-compose logs bot | grep Publicou

# Testar clock
docker-compose logs server | grep Clock

# Contar servidores ativos
docker-compose ps server | wc -l

# Ver heartbeats
docker-compose logs reference | grep heartbeat
```

## 💾 Backup de Dados

```bash
# Copiar dados para host
docker cp $(docker-compose ps -q server | head -1):/app/data ./backup

# Restaurar dados
docker cp ./backup/. $(docker-compose ps -q server | head -1):/app/data/

# Backup do volume
docker run --rm -v src_server-data:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz /data

# Restaurar volume
docker run --rm -v src_server-data:/data -v $(pwd):/backup alpine tar xzf /backup/data-backup.tar.gz -C /
```

## 🌐 Network

```bash
# Inspecionar network
docker network inspect src_messaging

# Ver IPs dos containers
docker-compose ps -q | xargs docker inspect -f '{{.Name}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'

# Testar conectividade
docker-compose exec client ping broker
docker-compose exec server ping reference
```

## 📝 Scripts Auxiliares

```bash
# Usando o script init.sh
cd src

# Iniciar
./scripts/init.sh start

# Parar
./scripts/init.sh stop

# Reiniciar
./scripts/init.sh restart

# Logs
./scripts/init.sh logs

# Cliente
./scripts/init.sh client

# Status
./scripts/init.sh status

# Limpar
./scripts/init.sh clean

# Escalar
./scripts/init.sh scale-servers 5
./scripts/init.sh scale-bots 10
```

## 🎯 Comandos Rápidos

```bash
# Setup inicial
cd src && docker-compose up --build -d

# Ver se está funcionando
docker-compose ps && docker-compose logs --tail=20

# Conectar cliente
docker-compose run --rm client node main.js

# Ver atividade
docker-compose logs -f server bot

# Parar tudo
docker-compose down

# Limpar e reiniciar
docker-compose down -v && docker-compose up --build -d
```

## 🔐 Troubleshooting

```bash
# Porta em uso
sudo lsof -i :5555
sudo lsof -i :5556

# Container não inicia
docker-compose logs [service_name]
docker-compose up [service_name]

# Rebuild forçado
docker-compose build --no-cache [service_name]
docker-compose up -d --force-recreate [service_name]

# Remover tudo e recomeçar
docker-compose down -v
docker system prune -af
docker-compose up --build
```

## 📚 Exemplos de Uso

### Cenário 1: Desenvolvimento
```bash
# Terminal 1 - Logs
cd src && docker-compose logs -f

# Terminal 2 - Sistema
docker-compose up --build

# Terminal 3 - Cliente
docker-compose run --rm client node main.js
```

### Cenário 2: Teste de Carga
```bash
# Aumentar bots
docker-compose up -d --scale bot=10

# Monitorar
docker stats
docker-compose logs -f bot
```

### Cenário 3: Teste de Replicação
```bash
# Terminal 1 - Ver replicação
docker-compose logs -f server | grep replic

# Terminal 2 - Cliente criando dados
docker-compose run --rm client node main.js
```

### Cenário 4: Teste de Falha
```bash
# Parar um servidor
docker-compose stop server

# Escalar para menos
docker-compose up -d --scale server=1

# Testar que sistema continua
docker-compose run --rm client node main.js

# Reestabelecer
docker-compose up -d --scale server=3
```

---

**Salve este arquivo para referência rápida!**

