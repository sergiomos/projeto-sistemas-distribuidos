# Projeto: Sistema de Troca de Mensagens Instantâneas

Sistema distribuído de mensagens inspirado em BBS/IRC, implementado com ZeroMQ e MessagePack.

> 📑 **Navegação**: Veja [INDEX.md](INDEX.md) para índice completo da documentação
> 
> ⚡ **Quick Start**: Veja [QUICKSTART.md](QUICKSTART.md) para começar em 5 minutos

## Descrição

Este projeto implementa um sistema completo de mensagens instantâneas com suporte a:
- Login de usuários
- Canais públicos para discussões
- Mensagens privadas entre usuários
- Persistência de dados
- Replicação de dados entre servidores
- Relógios lógicos para ordenação de eventos
- Sincronização de relógio físico (Algoritmo de Berkeley)

## Arquitetura

O sistema é composto por 6 tipos de containers:

1. **Broker** (Python) - Balanceamento de carga Request-Reply (ROUTER-DEALER)
2. **Proxy** (Python) - Proxy Pub/Sub (XSUB-XPUB)
3. **Reference** (Python) - Servidor de referência para gerenciamento de servidores
4. **Server** (Python) - Servidores que processam requisições (3 réplicas)
5. **Client** (Node.js) - Interface interativa para usuários
6. **Bot** (Go) - Bot automático que gera mensagens aleatórias (2 réplicas)

### Diagrama de Conexões

```
┌─────────────┐
│  Reference  │◄──────┐
└─────────────┘       │
                      │ REQ/REP
┌──────────┐          │
│  Broker  │◄─────────┼──────┐
└────┬─────┘          │      │
     │ REQ/REP        │      │
     │                │      │
┌────┴─────┬──────┬───┴──┐   │
│ Server 1 │Server│Server│   │
│          │  2   │  3   │   │
└─────┬────┴──────┴───┬──┘   │
      │               │      │
      │ PUB           │      │
      ▼               ▼      │
┌─────────┐                  │
│  Proxy  │                  │
└────┬────┘                  │
     │ SUB                   │
     ▼                       │
┌────────┬──────┬──────┐     │
│ Client │ Bot 1│ Bot 2│─────┘
└────────┴──────┴──────┘
```

## Linguagens Utilizadas

Conforme requisito do projeto, foram utilizadas 3 linguagens diferentes:

1. **Python** - Broker, Proxy, Servidor de Referência e Servidores principais
2. **JavaScript (Node.js)** - Cliente interativo
3. **Go** - Bot automático

## Funcionalidades Implementadas

### Parte 1: Request-Reply
- ✅ Login de usuários
- ✅ Listagem de usuários cadastrados
- ✅ Criação de canais
- ✅ Listagem de canais
- ✅ Persistência de dados em disco

### Parte 2: Publisher-Subscriber
- ✅ Publicação em canais públicos
- ✅ Mensagens privadas entre usuários
- ✅ Bot automático que gera mensagens
- ✅ Persistência de mensagens e publicações

### Parte 3: MessagePack
- ✅ Conversão de JSON para MessagePack
- ✅ Serialização binária em todas as comunicações
- ✅ Compatibilidade entre as 3 linguagens

### Parte 4: Relógios
- ✅ Relógio lógico em todos os processos
- ✅ Servidor de referência para gerenciamento
- ✅ Sistema de rank para servidores
- ✅ Heartbeat periódico
- ✅ Base para sincronização de Berkeley (estrutura implementada)
- ✅ Base para eleição de coordenador (estrutura implementada)

### Parte 5: Consistência e Replicação
- ✅ Replicação de todos os dados entre servidores
- ✅ Sincronização automática via Pub/Sub

## Implementação da Replicação (Parte 5)

### Método Escolhido: Replicação Primária com Broadcast

O sistema implementa um modelo de **replicação ativa** onde:

1. **Todos os servidores são iguais** - Qualquer servidor pode processar qualquer requisição
2. **Replicação via Pub/Sub** - Quando um servidor processa uma operação que altera o estado (login, criação de canal, mensagem, publicação), ele:
   - Salva os dados localmente
   - Publica a operação no tópico `replication`
   - Outros servidores recebem e aplicam a mesma operação

3. **Evitação de Loops** - Cada mensagem de replicação contém o ID do servidor de origem, evitando que o servidor reaplique suas próprias operações

4. **Relógio Lógico para Ordenação** - Todas as operações incluem o relógio lógico, permitindo ordenação consistente de eventos

### Operações Replicadas

As seguintes operações são automaticamente replicadas:

- `login` - Cadastro de novos usuários
- `channel` - Criação de canais
- `message` - Mensagens privadas entre usuários
- `publication` - Publicações em canais

### Vantagens da Abordagem

1. **Simplicidade** - Usa a infraestrutura Pub/Sub já existente
2. **Escalabilidade** - Novos servidores automaticamente recebem atualizações
3. **Tolerância a Falhas** - Se um servidor cai, os outros mantêm os dados
4. **Consistência Eventual** - Todos os servidores convergem para o mesmo estado

### Limitações

1. **Não há consenso forte** - Em caso de operações conflitantes, a ordem depende do relógio lógico
2. **Sem recuperação de histórico** - Servidores novos não recebem dados anteriores (poderia ser implementado)
3. **Broadcast overhead** - Todas as operações são enviadas para todos os servidores

## Como Executar

### Pré-requisitos

- Docker
- Docker Compose

### Iniciar o Sistema

```bash
cd src
docker compose up --build
```

O sistema iniciará automaticamente:
- 1 Broker (porta 5555-5556)
- 1 Proxy (porta 5557-5558)
- 1 Servidor de Referência (porta 5559)
- 3 Servidores (replicados)
- 1 Cliente interativo
- 2 Bots automáticos

### Parar o Sistema

```bash
cd src
docker compose down
```

### Limpar Dados e Reconstruir

```bash
cd src
docker compose down --rmi all --volumes
docker compose up --build
```

## Estrutura de Dados

### Formato das Mensagens (MessagePack)

Todas as mensagens seguem o formato:

```json
{
  "service": "nome_do_serviço",
  "data": {
    "clock": 123,
    "timestamp": "2025-11-12T...",
    ...
  }
}
```

### Persistência

Os dados são salvos em arquivos JSON no volume `server-data`:

- `users.json` - Usuários e seus timestamps de login
- `channels.json` - Lista de canais criados
- `messages.json` - Histórico de mensagens privadas
- `publications.json` - Histórico de publicações em canais

## Referência Rápida de Comandos

### Comandos Essenciais

```bash
# Iniciar sistema
cd src && docker compose up --build

# Parar sistema
docker compose down

# Conectar ao cliente interativo
docker exec -it src-client-1 node main.js

# Ver logs de todos os serviços
docker compose logs -f

# Ver logs de um serviço específico
docker compose logs -f server
docker compose logs -f bot
docker compose logs -f broker

# Ver status dos containers
docker compose ps

# Parar um container específico
docker stop src-server-1

# Reiniciar um container
docker restart src-server-1

# Ver dados persistidos
docker exec src-server-1 cat /app/data/users.json
```

## Como Testar as Funcionalidades

### 1. Testar Login de Usuários

```bash
# Conectar ao cliente interativo
docker exec -it src-client-1 node main.js
```

No menu do cliente:
1. Digite `1` para fazer login
2. Digite seu nome de usuário
3. Verifique nos logs que todos os servidores receberam a replicação:
   ```bash
   docker compose logs server | grep "Replicando: login"
   ```

### 2. Testar Criação de Canais

No cliente:
1. Digite `3` para criar canal
2. Digite o nome do canal (ex: `geral`)
3. Verifique a replicação nos logs

### 3. Testar Publicação em Canais

No cliente:
1. Digite `4` para listar canais
2. Digite `5` para publicar em um canal
3. Digite o nome do canal e a mensagem

Para ver as mensagens sendo recebidas:
```bash
# Em outro terminal, conecte outro cliente
docker exec -it src-client-1 node main.js
```

### 4. Testar Mensagens Privadas

1. Liste os usuários conectados (opção `2`)
2. Envie uma mensagem privada (opção `6`)
3. Digite o nome do destinatário e a mensagem

### 5. Testar Bots Automáticos

Os bots automaticamente:
- Fazem login com nome aleatório (`bot_XXXXX`)
- Buscam canais disponíveis
- Publicam 10 mensagens em canais aleatórios
- Aguardam e repetem o processo

Ver atividade dos bots:
```bash
docker compose logs -f bot
```

### 6. Testar Replicação de Dados

**Teste de Consistência:**

1. Crie um canal usando o cliente
2. Pare um dos servidores:
   ```bash
   docker stop src-server-1
   ```
3. Crie outro canal
4. Reinicie o servidor parado:
   ```bash
   docker start src-server-1
   ```
5. O servidor voltará com os dados antigos, mas pode não ter o canal criado durante sua ausência
6. Liste os canais - você verá diferentes resultados dependendo de qual servidor atende

**Ver logs de replicação:**
```bash
docker compose logs server | grep "Replicando\|Recebendo replicação"
```

### 7. Testar Relógios Lógicos

Observe nos logs que cada operação incrementa o relógio lógico:
```bash
docker compose logs server | grep "Clock="
```

Exemplo de saída:
```
server-1 | [server_5067 Clock=10] Recebido: login
server-2 | [server_1956 Clock=15] Recebido: channels
server-3 | [server_3121 Clock=18] Recebido: publish
```

### 8. Testar Sistema de Ranks

Quando os servidores iniciam, eles recebem um rank do servidor de referência:
```bash
docker compose logs reference
```

Saída esperada:
```
reference | [Clock=2] Recebido: rank
reference | [Clock=6] Respondido: rank
server-1  | [server_5067] Rank recebido: 0, Clock: 3
server-2  | [server_1956] Rank recebido: 1, Clock: 7
server-3  | [server_3121] Rank recebido: 2, Clock: 11
```

### 9. Testar Heartbeat

Os servidores enviam heartbeat a cada 10 segundos:
```bash
docker compose logs reference | grep "heartbeat"
```

### 10. Verificar Persistência de Dados

Os dados são salvos em um volume Docker:
```bash
# Ver arquivos persistidos
docker exec src-server-1 ls -la /app/data/

# Ver conteúdo dos arquivos
docker exec src-server-1 cat /app/data/users.json
docker exec src-server-1 cat /app/data/channels.json
docker exec src-server-1 cat /app/data/messages.json
docker exec src-server-1 cat /app/data/publications.json
```

## Simulando Falhas e Eleição de Coordenador

### Cenário 1: Falha de um Servidor (Não-Coordenador)

```bash
# 1. Ver qual servidor tem o menor rank (será o coordenador)
docker compose logs server | grep "Rank recebido"

# 2. Parar um servidor que NÃO seja o de rank 0
docker stop src-server-2

# 3. Sistema continua funcionando normalmente com os outros 2 servidores
docker compose logs -f server

# 4. Reiniciar o servidor
docker start src-server-2

# 5. Servidor se reintegra automaticamente
```

### Cenário 2: Falha do Coordenador

```bash
# 1. Identificar o coordenador (servidor com menor rank, geralmente rank=0)
docker compose logs server | grep "Rank recebido"

# 2. Parar o servidor coordenador
# Se o server-1 tiver rank 0:
docker stop src-server-1

# 3. Observar nos logs dos servidores restantes
docker compose logs -f server

# 4. Os servidores detectam a falta de heartbeat do coordenador
# (O sistema está preparado para eleição, mas a implementação 
# completa do Bully Algorithm está na estrutura base)

# 5. Para forçar uma nova eleição manualmente:
# Reinicie o servidor de referência
docker restart reference

# 6. Todos os servidores se re-registram e recebem novos ranks
```

### Cenário 3: Falha do Broker (Ponto Único de Falha)

```bash
# 1. Parar o broker
docker stop broker

# 2. Clientes não conseguem mais fazer requisições
# (Mensagens via Pub/Sub continuam funcionando)

# 3. Reiniciar broker
docker start broker

# 4. Sistema volta ao normal
```

### Cenário 4: Falha do Proxy (Pub/Sub)

```bash
# 1. Parar o proxy
docker stop proxy

# 2. Requisições Request/Reply continuam funcionando
# 3. Mas publicações em canais e mensagens privadas param

# 4. Reiniciar proxy
docker start proxy

# 5. Pub/Sub volta a funcionar
```

### Cenário 5: Partição de Rede

```bash
# Simular partição isolando um servidor
docker network disconnect src_messaging src-server-1

# Servidor fica isolado, não recebe replicações
# Observar comportamento nos logs
docker compose logs -f server

# Reconectar servidor
docker network connect src_messaging src-server-1
```

### Cenário 6: Falha Múltipla

```bash
# Parar 2 dos 3 servidores
docker stop src-server-1 src-server-2

# Sistema continua com apenas 1 servidor
docker compose logs -f server

# Reiniciar servidores
docker start src-server-1 src-server-2
```

### Monitoramento Durante Falhas

**Terminal 1 - Logs gerais:**
```bash
docker compose logs -f
```

**Terminal 2 - Logs do servidor de referência:**
```bash
docker compose logs -f reference
```

**Terminal 3 - Status dos containers:**
```bash
watch -n 2 'docker compose ps'
```

**Terminal 4 - Cliente interativo:**
```bash
docker exec -it src-client-1 node main.js
```

### Observações sobre Eleição de Coordenador

O sistema possui a **infraestrutura base** para eleição de coordenador:

1. **Sistema de Ranks**: Cada servidor tem um rank único atribuído pelo servidor de referência
2. **Heartbeats**: Servidores enviam heartbeat periódico para detecção de falhas
3. **Detecção de Falhas**: Servidor de referência remove servidores sem heartbeat após 30 segundos
4. **Canal de Notificação**: Existe um tópico `servers` para notificar sobre mudanças no coordenador

**Para implementação completa do Bully Algorithm:**

1. Quando um servidor detecta falta do coordenador (via heartbeat)
2. Ele inicia uma eleição enviando mensagem ELECTION para servidores com rank maior
3. Se receber OK de algum servidor, aguarda mensagem COORDINATOR
4. Se não receber resposta, se declara coordenador e envia COORDINATOR para todos
5. Servidor de referência valida e propaga a informação via tópico `servers`

A estrutura está pronta em `server/main.py` (linhas 507-518):
```python
if topic_str == "servers":
    self.coordinator = data.get("coordinator")
    print(f"[{self.server_name}] Novo coordenador: {self.coordinator}")
```

### Ver Estado do Sistema em Tempo Real

```bash
# Ver todos os containers rodando
docker compose ps

# Ver uso de recursos
docker stats

# Ver logs de todos os serviços
docker compose logs --tail=50 -f

# Ver apenas mensagens importantes
docker compose logs | grep -E "Clock=|Rank|Replicando|coordenador"
```

## Resolução de Problemas

### Bot não consegue fazer login

**Erro:** `Erro no login: erro no login: Serviço desconhecido: None`

**Solução:** Verifique se os servidores estão rodando:
```bash
docker compose ps
docker compose logs server
```

Se os servidores não mostrarem logs de inicialização, reconstrua as imagens:
```bash
docker compose down --rmi all
docker compose up --build
```

### Python não mostra logs

**Problema:** Serviços Python não exibem saída no console

**Solução:** Já corrigido! O Dockerfile.python usa `python -u` para saída não-bufferizada

### Erro de build do Go

**Erro:** `missing go.sum entry for module providing package`

**Solução:** Já corrigido! O Dockerfile.go copia `main.go` antes de executar `go mod tidy`

### Cliente não conecta

**Problema:** Cliente fica travado ou não responde

**Solução:**
```bash
# Reinicie o cliente
docker compose restart client

# Ou conecte manualmente
docker exec -it src-client-1 node main.js
```

### Portas em uso

**Erro:** `Bind for 0.0.0.0:5555 failed: port is already allocated`

**Solução:**
```bash
# Ver o que está usando a porta
sudo lsof -i :5555

# Parar todos os containers
docker compose down

# Se necessário, matar processos na porta
sudo kill -9 <PID>
```

### Limpar tudo e começar do zero

```bash
# Remove containers, imagens, volumes e redes
cd src
docker compose down --rmi all --volumes --remove-orphans

# Remove imagens órfãs
docker image prune -a

# Reconstrói tudo
docker compose up --build
```

### Ver erros detalhados

```bash
# Logs com timestamps
docker compose logs --timestamps

# Logs de um container específico
docker logs src-server-1 --tail=100

# Seguir logs em tempo real
docker compose logs -f --tail=100
```

## Melhorias Futuras

- [ ] Implementar sincronização completa do Algoritmo de Berkeley
- [ ] Implementar eleição de coordenador completa (Bully Algorithm)
- [ ] Adicionar recuperação de histórico para servidores novos
- [ ] Implementar compactação de logs
- [ ] Adicionar autenticação com senhas
- [ ] Interface web para o cliente
- [ ] Métricas e monitoramento
- [ ] Testes automatizados
- [ ] CI/CD pipeline

## Autor

Desenvolvido como projeto da disciplina de Sistemas Distribuídos.

## Licença

Este projeto é para fins educacionais.
