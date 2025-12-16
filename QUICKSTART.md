# Quick Start - Sistema de Mensagens Distribuído

Comece a usar o sistema em 5 minutos!

## Passo 1: Iniciar o Sistema

```bash
cd src
docker compose up --build
```

Aguarde até ver as mensagens:
```
broker      | Broker iniciado - Balanceamento de carga entre clientes e servidores
proxy       | Proxy Pub/Sub iniciado
reference   | Servidor de referência iniciado na porta 5559
server-1    | Servidor server_XXXX (rank=0) iniciado, Clock: X
server-2    | Servidor server_XXXX (rank=1) iniciado, Clock: X
server-3    | Servidor server_XXXX (rank=2) iniciado, Clock: X
bot-1       | Bot logado: bot_XXXXX
bot-2       | Bot logado: bot_XXXXX
```

## Passo 2: Conectar ao Cliente

Em outro terminal:

```bash
docker exec -it src-client-1 node main.js
```

## Passo 3: Fazer Login

No menu do cliente:
```
Digite sua opção: 1
Digite seu nome de usuário: alice
```

Você verá: `Login realizado com sucesso!`

## Passo 4: Criar um Canal

```
Digite sua opção: 3
Digite o nome do canal: geral
```

Você verá: `Canal criado com sucesso!`

## Passo 5: Publicar uma Mensagem

```
Digite sua opção: 5
Digite o nome do canal: geral
Digite a mensagem: Olá, mundo!
```

Você verá sua mensagem sendo publicada!

## Passo 6: Ver os Bots em Ação

Os bots automáticos já estão publicando mensagens. Observe no terminal principal:

```
bot-1  | [Clock=X] [geral] Publicou: Olá, sou um bot!
bot-2  | [Clock=X] [geral] Publicou: Mensagem automática
```

## Passo 7: Testar Replicação

Em outro terminal, veja os logs dos servidores:

```bash
docker compose logs server | grep "Replicando"
```

Você verá que todas as operações são replicadas entre os 3 servidores!

## Comandos Úteis

### Ver todos os logs
```bash
docker compose logs -f
```

### Ver logs de um serviço específico
```bash
docker compose logs -f server
docker compose logs -f bot
```

### Ver dados persistidos
```bash
docker exec src-server-1 cat /app/data/users.json
docker exec src-server-1 cat /app/data/channels.json
```

### Parar o sistema
```bash
docker compose down
```

### Recomeçar do zero
```bash
docker compose down --rmi all --volumes
docker compose up --build
```

## Menu do Cliente

```
=== Sistema de Mensagens ===
1. Login
2. Listar usuários
3. Criar canal
4. Listar canais
5. Publicar em canal
6. Enviar mensagem privada
0. Sair
```

## Próximos Passos

- Leia o [README.md](README.md) completo para entender a arquitetura
- Veja a seção "Como Testar as Funcionalidades" para testes avançados
- Experimente simular falhas de servidores
- Observe os relógios lógicos e a replicação em ação

## Problemas?

Se algo não funcionar:

1. Verifique se todas as portas estão livres (5555-5559)
2. Certifique-se de ter Docker Compose v2 instalado
3. Veja a seção "Resolução de Problemas" no README.md
4. Limpe tudo e reconstrua: `docker compose down --rmi all --volumes && docker compose up --build`

## Exemplo de Sessão Completa

```bash
# Terminal 1: Iniciar sistema
cd src
docker compose up --build

# Terminal 2: Cliente Alice
docker exec -it src-client-1 node main.js
# Digite: 1 (login)
# Nome: alice
# Digite: 3 (criar canal)
# Canal: geral
# Digite: 5 (publicar)
# Canal: geral
# Mensagem: Olá pessoal!

# Terminal 3: Ver logs
docker compose logs -f server | grep "Clock="

# Terminal 4: Ver replicação
docker compose logs server | grep -E "Replicando|Recebendo replicação"
```

Pronto! Agora você tem um sistema de mensagens distribuído completo rodando! 🚀

