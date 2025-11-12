# Guia de Testes

Este documento descreve como testar todas as funcionalidades do sistema.

## 1. Iniciar o Sistema

```bash
cd src
docker-compose up --build
```

Aguarde todos os containers iniciarem. Você deve ver logs de:
- Broker iniciado
- Proxy iniciado
- Reference iniciado
- 3 servidores iniciados (com seus ranks)
- 2 bots gerando mensagens

## 2. Teste Básico - Login e Canais

### 2.1 Conectar ao Cliente

Em um novo terminal:

```bash
docker-compose exec client node main.js
```

### 2.2 Fazer Login

Digite um nome de usuário quando solicitado, por exemplo: `usuario1`

Você deve ver: `Login bem-sucedido: usuario1`

### 2.3 Criar Canal

No menu, escolha opção `2` e crie um canal: `geral`

### 2.4 Listar Canais

Escolha opção `3` para ver todos os canais disponíveis

### 2.5 Verificar Replicação

Nos logs dos servidores, você deve ver:
- Um servidor processou a criação do canal
- Os outros servidores receberam a replicação

```bash
docker-compose logs server | grep -i replicando
```

## 3. Teste de Publicação em Canais

### 3.1 Inscrever em Canal

No cliente, escolha opção `4` e inscreva-se no canal `geral`

### 3.2 Publicar Mensagem

Escolha opção `5`, canal `geral`, e envie uma mensagem

### 3.3 Ver Mensagens dos Bots

Você deve ver mensagens automáticas dos bots aparecendo no seu cliente

## 4. Teste de Mensagens Privadas

### 4.1 Segundo Cliente

Em outro terminal, conecte um segundo cliente:

```bash
docker-compose run --rm client node main.js
```

Faça login como `usuario2`

### 4.2 Listar Usuários

No segundo cliente, escolha opção `1` para ver todos os usuários

Você deve ver `usuario1` e `usuario2` na lista (além dos bots)

### 4.3 Enviar Mensagem Privada

No segundo cliente, escolha opção `6`
- Para usuário: `usuario1`
- Mensagem: `Olá!`

### 4.4 Verificar Recebimento

No primeiro cliente, você deve ver:
```
[MSG de usuario2]: Olá!
```

## 5. Teste de Relógios Lógicos

### 5.1 Observar Clock nas Mensagens

Todas as mensagens exibidas mostram o clock lógico:
```
[Clock=25] [geral] bot_1234: Mensagem automática
```

### 5.2 Verificar Incremento

O clock deve sempre aumentar:
- Antes de enviar requisição
- Ao receber resposta
- Ao receber publicação

## 6. Teste de Replicação

### 6.1 Parar um Servidor

```bash
docker-compose stop server
docker-compose up -d --scale server=2 server
```

### 6.2 Criar Novo Canal

Com apenas 2 servidores, crie um canal `teste`

### 6.3 Reiniciar Servidor

```bash
docker-compose up -d --scale server=3 server
```

### 6.4 Verificar Dados

O novo servidor deve receber replicações futuras, mas não histórico anterior

## 7. Teste de Servidor de Referência

### 7.1 Ver Ranks dos Servidores

Nos logs:

```bash
docker-compose logs server | grep -i rank
```

Você deve ver cada servidor recebendo um rank único (0, 1, 2)

### 7.2 Ver Heartbeats

```bash
docker-compose logs reference | grep -i heartbeat
```

Deve mostrar heartbeats periódicos de cada servidor

## 8. Teste de Persistência

### 8.1 Criar Dados

Faça login, crie canais, envie mensagens

### 8.2 Reiniciar Sistema

```bash
docker-compose down
docker-compose up -d
```

### 8.3 Verificar Dados

Conecte um cliente e liste usuários e canais - devem estar preservados

## 9. Teste de Carga (Bots)

### 9.1 Observar Bots

Os bots automaticamente:
- Fazem login
- Buscam canais
- Publicam mensagens

```bash
docker-compose logs -f bot
```

### 9.2 Aumentar Réplicas de Bots

```bash
docker-compose up -d --scale bot=5
```

Observe o aumento de mensagens no sistema

## 10. Verificar MessagePack

### 10.1 Capturar Tráfego

As mensagens estão em formato binário (MessagePack), não JSON

### 10.2 Verificar Tamanho

MessagePack deve produzir mensagens menores que JSON equivalente

## Resultados Esperados

- ✅ Login funcionando
- ✅ Canais sendo criados e listados
- ✅ Mensagens privadas sendo entregues
- ✅ Publicações em canais visíveis para inscritos
- ✅ Bots gerando mensagens automaticamente
- ✅ Relógio lógico incrementando corretamente
- ✅ Replicação de dados entre servidores
- ✅ Ranks únicos para cada servidor
- ✅ Heartbeats periódicos
- ✅ Dados persistidos entre reinicializações

## Troubleshooting

### Cliente não conecta

```bash
# Verificar se broker está rodando
docker-compose ps

# Reiniciar broker
docker-compose restart broker
```

### Servidor não recebe mensagens

```bash
# Verificar logs
docker-compose logs server

# Reiniciar servidor
docker-compose restart server
```

### Bot com erro

```bash
# Ver erro específico
docker-compose logs bot

# Recriar bot
docker-compose up -d --force-recreate bot
```

## Limpeza

Para limpar todos os dados e containers:

```bash
docker-compose down -v
docker system prune -f
```

