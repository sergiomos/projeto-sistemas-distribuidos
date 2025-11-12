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
docker-compose up --build
```

### Conectar ao Cliente

```bash
docker-compose exec client node main.js
```

### Ver Logs dos Servidores

```bash
docker-compose logs -f server
```

### Ver Logs dos Bots

```bash
docker-compose logs -f bot
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

## Testes

### Testar Replicação

1. Inicie o sistema
2. Conecte com um cliente e faça login
3. Verifique nos logs que todos os 3 servidores receberam a replicação
4. Crie um canal em um cliente
5. Conecte outro cliente e liste os canais (deve ver o canal criado, mesmo que atendido por servidor diferente)

### Testar Bots

Os bots automaticamente:
1. Fazem login com nome aleatório
2. Buscam canais disponíveis
3. Publicam 10 mensagens em um canal aleatório
4. Repetem o processo

## Melhorias Futuras

- [ ] Implementar sincronização completa do Algoritmo de Berkeley
- [ ] Implementar eleição de coordenador (Bully Algorithm)
- [ ] Adicionar recuperação de histórico para servidores novos
- [ ] Implementar compactação de logs
- [ ] Adicionar autenticação com senhas
- [ ] Interface web para o cliente
- [ ] Métricas e monitoramento

## Autor

Desenvolvido como projeto da disciplina de Sistemas Distribuídos.

## Licença

Este projeto é para fins educacionais.
