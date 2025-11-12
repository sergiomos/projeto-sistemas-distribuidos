# Arquitetura do Sistema

## Visão Geral

O sistema implementa uma arquitetura de microserviços distribuídos usando padrões de mensageria ZeroMQ.

## Componentes

### 1. Broker (Python)
**Padrão**: ROUTER-DEALER (Balanceamento de Carga)

**Responsabilidades**:
- Recebe requisições dos clientes (porta 5555)
- Distribui requisições entre servidores usando round-robin (porta 5556)
- Balanceamento automático de carga

**Portas**:
- 5555: Clientes conectam (ROUTER)
- 5556: Servidores conectam (DEALER)

**Código**: `src/broker/main.py`

---

### 2. Proxy (Python)
**Padrão**: XSUB-XPUB (Pub/Sub Proxy)

**Responsabilidades**:
- Recebe publicações dos servidores (porta 5557)
- Distribui publicações para subscritores (porta 5558)
- Gerencia tópicos de canais e mensagens privadas

**Portas**:
- 5557: Publishers conectam (XSUB)
- 5558: Subscribers conectam (XPUB)

**Tópicos**:
- `[nome_do_canal]`: Publicações em canais
- `[nome_do_usuario]`: Mensagens privadas
- `servers`: Eleição de coordenador
- `replication`: Replicação de dados

**Código**: `src/proxy/main.py`

---

### 3. Reference Server (Python)
**Padrão**: REQ-REP

**Responsabilidades**:
- Atribuir ranks únicos aos servidores
- Manter lista de servidores ativos
- Receber heartbeats periódicos
- Fornecer lista de servidores para sincronização

**Porta**: 5559

**Serviços**:
- `rank`: Atribui rank para novo servidor
- `list`: Retorna lista de servidores ativos
- `heartbeat`: Atualiza status de servidor

**Código**: `src/reference/main.py`

---

### 4. Server (Python) - 3 Réplicas
**Padrões**: REP (requisições), PUB (publicações), SUB (replicação)

**Responsabilidades**:
- Processar requisições de clientes
- Gerenciar usuários e canais
- Publicar mensagens em canais
- Replicar dados para outros servidores
- Manter relógio lógico

**Conexões**:
- REP → Broker (5556)
- PUB → Proxy (5557)
- SUB → Proxy (5558)
- REQ → Reference (5559)

**Serviços Implementados**:

#### `login`
Registra usuário no sistema
```json
Request:
{
  "service": "login",
  "data": {
    "user": "nome_usuario",
    "timestamp": "2025-11-12T...",
    "clock": 10
  }
}

Response:
{
  "service": "login",
  "data": {
    "status": "sucesso",
    "timestamp": "2025-11-12T...",
    "clock": 11
  }
}
```

#### `users`
Lista usuários cadastrados
```json
Request:
{
  "service": "users",
  "data": {
    "timestamp": "...",
    "clock": 12
  }
}

Response:
{
  "service": "users",
  "data": {
    "users": ["user1", "user2"],
    "timestamp": "...",
    "clock": 13
  }
}
```

#### `channel`
Cria novo canal
```json
Request:
{
  "service": "channel",
  "data": {
    "channel": "geral",
    "timestamp": "...",
    "clock": 14
  }
}

Response:
{
  "service": "channel",
  "data": {
    "status": "sucesso",
    "timestamp": "...",
    "clock": 15
  }
}
```

#### `channels`
Lista canais disponíveis
```json
Request:
{
  "service": "channels",
  "data": {
    "timestamp": "...",
    "clock": 16
  }
}

Response:
{
  "service": "channels",
  "data": {
    "channels": ["geral", "tech"],
    "timestamp": "...",
    "clock": 17
  }
}
```

#### `publish`
Publica mensagem em canal
```json
Request:
{
  "service": "publish",
  "data": {
    "user": "user1",
    "channel": "geral",
    "message": "Olá!",
    "timestamp": "...",
    "clock": 18
  }
}

Response:
{
  "service": "publish",
  "data": {
    "status": "OK",
    "timestamp": "...",
    "clock": 19
  }
}

Publication (no tópico "geral"):
{
  "user": "user1",
  "message": "Olá!",
  "timestamp": "...",
  "clock": 19
}
```

#### `message`
Envia mensagem privada
```json
Request:
{
  "service": "message",
  "data": {
    "src": "user1",
    "dst": "user2",
    "message": "Oi!",
    "timestamp": "...",
    "clock": 20
  }
}

Response:
{
  "service": "message",
  "data": {
    "status": "OK",
    "timestamp": "...",
    "clock": 21
  }
}

Publication (no tópico "user2"):
{
  "src": "user1",
  "message": "Oi!",
  "timestamp": "...",
  "clock": 21
}
```

**Código**: `src/server/main.py`

---

### 5. Client (Node.js)
**Padrões**: REQ (requisições), SUB (recebimento)

**Responsabilidades**:
- Interface interativa com usuário
- Enviar requisições ao broker
- Receber mensagens e publicações
- Manter relógio lógico

**Conexões**:
- REQ → Broker (5555)
- SUB → Proxy (5558)

**Menu**:
1. Listar usuários
2. Criar canal
3. Listar canais
4. Inscrever em canal
5. Publicar em canal
6. Enviar mensagem privada
7. Sair

**Código**: `src/client/main.js`

---

### 6. Bot (Go) - 2 Réplicas
**Padrões**: REQ (requisições), SUB (recebimento)

**Responsabilidades**:
- Gerar mensagens automaticamente
- Testar sistema sob carga
- Demonstrar funcionamento

**Comportamento**:
1. Login com nome aleatório (`bot_XXXXX`)
2. Loop infinito:
   - Buscar canais disponíveis
   - Escolher canal aleatório
   - Enviar 10 mensagens
   - Aguardar 2 segundos

**Mensagens**:
- "Olá, sou um bot!"
- "Mensagem automática"
- "Testando o sistema"
- "Bot em ação"
- "Mensagem de teste"
- "Sistema funcionando"
- "Publicação automática"
- "Bot ativo"
- "Teste de carga"
- "Mensagem gerada automaticamente"

**Código**: `src/bot/main.go`

---

## Fluxos de Dados

### Fluxo de Requisição (Request-Reply)

```
Cliente → Broker → Servidor → Broker → Cliente
[REQ]     [ROUTER] [REP]      [DEALER] [REP]
          [DEALER]             [ROUTER]
```

**Exemplo: Login**
1. Cliente envia `login` ao Broker
2. Broker encaminha para Servidor disponível (round-robin)
3. Servidor processa, atualiza clock, salva dados
4. Servidor responde ao Broker
5. Broker encaminha resposta ao Cliente
6. Cliente atualiza clock

### Fluxo de Publicação (Pub/Sub)

```
Servidor → Proxy → Clientes/Bots
[PUB]      [XSUB]  [SUB]
           [XPUB]
```

**Exemplo: Mensagem em Canal**
1. Cliente envia requisição `publish` ao Servidor
2. Servidor valida canal
3. Servidor publica no tópico do canal via Proxy
4. Proxy distribui para todos inscritos no canal
5. Clientes recebem e exibem mensagem

### Fluxo de Replicação

```
Servidor A → Proxy → Servidores B, C
[PUB]        [XSUB]  [SUB: replication]
(replication) [XPUB]
```

**Exemplo: Criação de Canal**
1. Servidor A recebe requisição `channel`
2. Servidor A cria canal localmente
3. Servidor A publica no tópico `replication`
4. Servidores B e C recebem replicação
5. Servidores B e C criam canal localmente
6. Todos os servidores têm o mesmo estado

---

## Relógios Lógicos

### Implementação

Todos os processos (cliente, bot, servidor) mantêm um relógio lógico:

**Regras**:
1. **Antes de enviar**: Incrementa clock
2. **Ao receber**: `clock = max(clock_local, clock_recebido) + 1`
3. **Todas as mensagens** incluem o clock

**Exemplo**:
```
Cliente (clock=5) → envia requisição (clock=6)
Servidor (clock=10) → recebe, atualiza para max(10,6)+1=11
Servidor (clock=11) → processa
Servidor (clock=12) → envia resposta (clock=12)
Cliente (clock=6) → recebe, atualiza para max(6,12)+1=13
```

### Ordenação de Eventos

Com relógios lógicos, é possível ordenar eventos:
- Se `clock_A < clock_B`, então A aconteceu antes de B
- Se `clock_A = clock_B`, usar outro critério (ex: timestamp)

---

## Persistência

### Arquivos JSON

Cada servidor mantém 4 arquivos:

1. **users.json**
```json
{
  "user1": ["2025-11-12T10:00:00Z", "2025-11-12T15:30:00Z"],
  "user2": ["2025-11-12T11:00:00Z"]
}
```

2. **channels.json**
```json
["geral", "tech", "random"]
```

3. **messages.json**
```json
[
  {
    "src": "user1",
    "dst": "user2",
    "message": "Oi!",
    "timestamp": "2025-11-12T10:05:00Z",
    "clock": 25
  }
]
```

4. **publications.json**
```json
[
  {
    "channel": "geral",
    "user": "user1",
    "message": "Olá todos!",
    "timestamp": "2025-11-12T10:10:00Z",
    "clock": 30
  }
]
```

### Volume Docker

Os dados são persistidos em um volume Docker:
```yaml
volumes:
  server-data:/app/data
```

---

## Replicação

### Estratégia

**Tipo**: Replicação Ativa (Active Replication)

**Mecanismo**:
1. Servidor primário processa operação
2. Servidor publica no tópico `replication`
3. Servidores secundários recebem e aplicam
4. Todos convergem para mesmo estado

**Operações Replicadas**:
- `login`: Novo usuário
- `channel`: Novo canal
- `message`: Mensagem privada
- `publication`: Publicação em canal

**Formato de Replicação**:
```json
{
  "operation": "login",
  "data": {
    "user": "user1",
    "timestamp": "..."
  },
  "server": "server_1234",
  "clock": 42
}
```

**Prevenção de Loops**:
- Cada replicação inclui `server` (origem)
- Servidor ignora replicações próprias
- `if source_server == self.server_name: return`

### Vantagens

- ✅ Tolerância a falhas
- ✅ Escalabilidade horizontal
- ✅ Consistência eventual
- ✅ Sem ponto único de falha

### Limitações

- ⚠️ Latência de replicação
- ⚠️ Overhead de rede
- ⚠️ Sem recuperação de histórico para novos servidores
- ⚠️ Conflitos resolvidos por timestamp/clock

---

## Serialização

### MessagePack

Todas as mensagens usam **MessagePack** em vez de JSON:

**Vantagens**:
- Tamanho menor (binário)
- Parsing mais rápido
- Compatível entre linguagens

**Bibliotecas**:
- Python: `msgpack`
- Node.js: `msgpack-lite`
- Go: `github.com/vmihailenco/msgpack/v5`

**Exemplo**:
```python
# Python
import msgpack
data = {"service": "login", "data": {...}}
packed = msgpack.packb(data)
socket.send(packed)

# Recebimento
received = socket.recv()
unpacked = msgpack.unpackb(received, raw=False)
```

---

## Escalabilidade

### Servidores

Configurado para 3 réplicas por padrão:
```yaml
deploy:
  replicas: 3
```

Pode ser escalado:
```bash
docker-compose up -d --scale server=5
```

### Bots

Configurado para 2 réplicas:
```yaml
deploy:
  replicas: 2
```

Pode ser escalado:
```bash
docker-compose up -d --scale bot=10
```

### Clientes

Ilimitados - cada cliente conecta independentemente

---

## Segurança

⚠️ **Este é um protótipo educacional**

Limitações de segurança:
- Sem autenticação (apenas nome de usuário)
- Sem criptografia
- Sem validação de permissões
- Sem proteção contra flood

Para produção, adicionar:
- Autenticação (JWT, OAuth)
- TLS/SSL para comunicação
- Rate limiting
- Validação de input
- Logs de auditoria

---

## Monitoramento

### Logs

Ver logs de todos os componentes:
```bash
docker-compose logs -f
```

Por componente:
```bash
docker-compose logs -f server
docker-compose logs -f broker
docker-compose logs -f bot
```

### Métricas

Servidor exibe:
- Relógio lógico atual
- Operações processadas
- Replicações enviadas/recebidas

Exemplo de log:
```
[server_1234 Clock=42] Recebido: login
[server_1234] Replicando: login
[server_5678] Recebendo replicação de server_1234: login
```

---

## Evolução Futura

### Fase 1 (Implementado)
- ✅ Request-Reply básico
- ✅ Pub/Sub
- ✅ MessagePack
- ✅ Relógios lógicos
- ✅ Replicação

### Fase 2 (Planejado)
- [ ] Sincronização de Berkeley completa
- [ ] Eleição de líder (Bully)
- [ ] Recuperação de histórico
- [ ] Compactação de logs

### Fase 3 (Futuro)
- [ ] Autenticação e autorização
- [ ] Interface web
- [ ] API REST
- [ ] Métricas e dashboards
- [ ] Testes automatizados

