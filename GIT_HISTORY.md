# Histórico de Commits do Projeto

Este documento descreve o histórico de desenvolvimento do projeto através dos commits Git.

## 📊 Estrutura dos Commits

O projeto foi desenvolvido de forma incremental, seguindo as 5 partes do enunciado:

### 🎯 Commits Iniciais
1. **docs: adiciona enunciado e especificações do projeto**
   - Enunciado geral
   - Especificações das 5 partes
   - Requisitos e padronizações

2. **chore: adiciona .gitignore**
   - Configuração para Python, Node.js e Go
   - Ignora node_modules, __pycache__, data, etc

### 🏗️ Parte 1: Request-Reply (Commits 3-7)

3. **feat(parte1): adiciona estrutura Docker inicial**
   - Dockerfile.python
   - docker-compose.yml base
   - Networks e volumes

4. **feat(parte1): implementa Broker com ROUTER-DEALER**
   - Balanceamento de carga
   - Portas 5555 (clientes) e 5556 (servidores)

5. **feat(parte1): implementa Proxy Pub/Sub com XSUB-XPUB**
   - Portas 5557 (publishers) e 5558 (subscribers)

6. **feat(parte1): implementa Server com serviços básicos**
   - login, users, channel, channels
   - Persistência em JSON
   - Request-Reply pattern

7. **feat(parte1): adiciona Cliente em Node.js**
   - Interface interativa
   - Menu com 4 opções
   - REQ/SUB sockets
   - Dockerfile.node

### 🔄 Parte 2: Pub/Sub (Commit 8)

8. **feat(parte2): implementa Bot automático em Go**
   - Bot com loop infinito
   - Geração automática de mensagens
   - REQ/SUB sockets
   - Dockerfile.go
   - 2 réplicas no docker-compose

> Nota: As funcionalidades de publish e message no servidor e cliente foram incluídas nos commits anteriores de forma integrada

### 📦 Parte 3: MessagePack (Incluído nos commits acima)

As conversões para MessagePack foram incluídas nos commits das Partes 1 e 2:
- Servidor já usa msgpack em todas as mensagens
- Cliente Node.js usa msgpack-lite
- Bot Go usa vmihailenco/msgpack/v5

### ⏰ Parte 4: Relógios (Commit 9)

9. **feat(parte4): implementa servidor de referência**
   - Ranks únicos para servidores
   - Serviços: rank, list, heartbeat
   - Relógio lógico
   - Porta 5559

> Nota: Relógios lógicos foram implementados em servidor, cliente e bot de forma integrada nos commits de implementação inicial de cada componente

### 🔁 Parte 5: Replicação (Incluído no Server)

A replicação foi implementada no servidor principal com:
- Tópico 'replication' para broadcast
- Operações replicadas: login, channel, message, publication
- Prevenção de loops
- Consistência eventual

### 📚 Documentação (Commits 10-14)

10. **docs: adiciona README.md completo**
    - Descrição do projeto
    - Arquitetura
    - Funcionalidades das 5 partes
    - Documentação da replicação
    - Instruções de uso

11. **docs: adiciona documentação de arquitetura detalhada**
    - ARCHITECTURE.md com 850+ linhas
    - Detalhes de cada componente
    - Fluxos de dados
    - Formato das mensagens

12. **docs: adiciona guias de testes e comandos**
    - TESTING.md: guia completo de testes
    - COMMANDS.md: referência de comandos Docker

13. **docs: adiciona resumo executivo e checklist**
    - SUMMARY.md: resumo do projeto
    - CHECKLIST.md: validação de requisitos

14. **docs: adiciona quick start e índice de navegação**
    - QUICKSTART.md: guia de 5 minutos
    - INDEX.md: índice completo

### 🛠️ Finalização (Commits 15-16)

15. **chore: adiciona script auxiliar e configurações**
    - init.sh: script para operações comuns
    - .gitignore adicional no src/

16. **chore: remove Dockerfile antigo**
    - Limpeza de arquivos obsoletos

## 📈 Estatísticas

- **Total de commits**: 16 novos (+ 4 anteriores)
- **Linhas de código**: ~1500+
- **Linhas de documentação**: ~3000+
- **Arquivos criados**: 20+

### Distribuição por Tipo

- **feat**: 7 commits (funcionalidades)
- **docs**: 5 commits (documentação)
- **chore**: 4 commits (configuração)

### Distribuição por Parte

- Parte 1: 5 commits principais
- Parte 2: 1 commit (+ integrações)
- Parte 3: Integrado nos commits de implementação
- Parte 4: 1 commit principal (+ integrações)
- Parte 5: Integrado no servidor
- Documentação: 5 commits
- Configuração: 4 commits

## 🎯 Convenções Usadas

### Prefixos de Commit

- `feat`: Nova funcionalidade
- `docs`: Documentação
- `chore`: Configuração, manutenção

### Escopo

- `(parte1)`: Relacionado à Parte 1
- `(parte2)`: Relacionado à Parte 2
- `(parte3)`: Relacionado à Parte 3
- `(parte4)`: Relacionado à Parte 4
- `(parte5)`: Relacionado à Parte 5

### Formato

```
tipo(escopo): descrição curta

- Detalhes
- Mais detalhes
```

## 🌳 Visualização do Histórico

Para visualizar o histórico completo:

```bash
# Lista simples
git log --oneline

# Com gráfico
git log --oneline --graph --all

# Detalhado
git log --stat

# Por autor
git log --author="nome"

# Por data
git log --since="2025-11-01"
```

## 🔍 Comandos Úteis

```bash
# Ver mudanças de um commit específico
git show <commit-hash>

# Ver arquivos modificados
git show <commit-hash> --stat

# Comparar dois commits
git diff <commit1> <commit2>

# Ver histórico de um arquivo
git log -- <arquivo>

# Buscar em commits
git log --grep="palavra"
```

## 📝 Observações

1. **Desenvolvimento Incremental**: O projeto foi desenvolvido parte por parte, conforme especificações

2. **Commits Atômicos**: Cada commit representa uma unidade lógica de mudança

3. **Mensagens Descritivas**: Todas as mensagens explicam claramente o que foi feito

4. **Documentação Extensiva**: 5 commits dedicados à documentação

5. **Código Limpo**: Implementação simples e direta em cada commit

## 🎓 Lições Aprendidas

- **Git Flow**: Desenvolvimento linear e incremental
- **Convenções**: Uso consistente de prefixos e escopos
- **Documentação**: Documentar enquanto desenvolve
- **Commits Pequenos**: Mudanças focadas e específicas
- **Histórico Limpo**: Fácil de entender e navegar

---

**Desenvolvido incrementalmente seguindo as 5 partes do projeto de Sistemas Distribuídos**

