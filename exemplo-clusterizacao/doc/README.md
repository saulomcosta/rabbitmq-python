Perfeito. Abaixo está o **README reescrito, unificado e organizado**, juntando **cluster + quorum queue + criação manual dos nós via variáveis de ambiente**, de forma **didática, progressiva e pronta para laboratório ou produção controlada**.

Você pode copiar e usar **diretamente no repositório**.

***

# 🐇 RabbitMQ em Cluster com **Quorum Queue**

## Alta Disponibilidade, Failover Automático e Tolerância a Falhas

Este guia demonstra **como criar manualmente um cluster RabbitMQ com 3 nós**, utilizando **variáveis de ambiente**, e como aplicar **Quorum Queues** para garantir:

✅ Alta disponibilidade
✅ Failover automático
✅ Consistência forte
✅ Nenhuma perda de mensagens

O conteúdo é voltado para **uso educacional, laboratórios locais e entendimento de cenários reais de produção**.

***

## 🎯 Objetivo do Guia

Demonstrar claramente:

*   Como subir **3 instâncias RabbitMQ independentes**
*   Como uni-las em **um único cluster**
*   Como o RabbitMQ **gerencia automaticamente falhas**
*   Como **Quorum Queues** funcionam em ambiente distribuído
*   Separação clara entre:
    *   **Infraestrutura (Cluster RabbitMQ)**
    *   **Código da aplicação (Producer / Consumer)**

***

## 🧱 Arquitetura do Cluster

    +------------+     +------------+     +------------+
    | RabbitMQ-1 |<--->| RabbitMQ-2 |<--->| RabbitMQ-3 |
    |  (Leader)  |     | (Follower) |     | (Follower) |
    +------------+     +------------+     +------------+

*   Apenas **um nó é líder da fila**
*   Os outros atuam como **réplicas**
*   Se o líder cair:
    ✅ Novo líder é eleito automaticamente
    ✅ Aplicações continuam funcionando

***

## ✅ Pré-requisitos

### Infraestrutura mínima recomendada

*   ✅ Linux ou macOS
*   ✅ RabbitMQ instalado
*   ✅ Erlang instalado
*   ✅ Plugin `rabbitmq_management` habilitado
*   ✅ Terminal aberto em **3 sessões diferentes** (ou 3 VMs)
*   ✅ Mesmo **Erlang Cookie** em todos os nós

Verificar RabbitMQ:

```bash
rabbitmq-server --version
```

***

## 🔐 1️⃣ Garantir o mesmo Erlang Cookie (**OBRIGATÓRIO**)

Todos os nós do cluster **devem usar exatamente o mesmo cookie**.

Arquivo padrão:

```text
~/.erlang.cookie
```

Permissões:

```bash
chmod 400 ~/.erlang.cookie
```

➡️ Copie o mesmo arquivo para todos os nós/sessões.

***

## 🧱 2️⃣ Criar o **Node 1** (Primeiro nó do cluster)

Abra o **Terminal 1**:

```bash
export RABBITMQ_NODENAME=rabbit@cluster1
export RABBITMQ_NODE_PORT=5672
export RABBITMQ_SERVER_START_ARGS='-rabbitmq_management listener [{port,15672}]'

rabbitmq-server start
```

✅ Nó inicial do cluster
✅ Management UI: <http://localhost:15672>

***

## 🧱 3️⃣ Criar o **Node 2** (Segundo nó)

Abra o **Terminal 2**:

```bash
export RABBITMQ_NODENAME=rabbit@cluster2
export RABBITMQ_NODE_PORT=5673
export RABBITMQ_SERVER_START_ARGS='-rabbitmq_management listener [{port,15673}]'

rabbitmq-server start
```

✅ UI: <http://localhost:15673>
❗ Ainda **não faz parte do cluster**

***

## 🧱 4️⃣ Criar o **Node 3** (Terceiro nó)

Abra o **Terminal 3**:

```bash
export RABBITMQ_NODENAME=rabbit@cluster3
export RABBITMQ_NODE_PORT=5674
export RABBITMQ_SERVER_START_ARGS='-rabbitmq_management listener [{port,15674}]'

rabbitmq-server start
```

✅ UI: <http://localhost:15674>
❗ Ainda **não faz parte do cluster**

***

## 🔗 5️⃣ Unir os nós ao cluster

Agora, vamos **juntar os nós secundários ao Node 1**.

### 🔁 Node 2

```bash
rabbitmqctl stop_app
rabbitmqctl reset
rabbitmqctl join_cluster rabbit@cluster1
rabbitmqctl start_app
```

### 🔁 Node 3

```bash
rabbitmqctl stop_app
rabbitmqctl reset
rabbitmqctl join_cluster rabbit@cluster1
rabbitmqctl start_app
```

***

## ✅ 6️⃣ Verificar o Cluster

Execute em qualquer nó:

```bash
rabbitmqctl cluster_status
```

Saída esperada:

```text
Nodes:
  rabbit@cluster1
  rabbit@cluster2
  rabbit@cluster3
```

✅ Cluster criado com sucesso
✅ Pronto para **Quorum Queue**

***

## 🧠 Por que 3 nós?

As **Quorum Queues utilizam o algoritmo Raft**, que exige maioria ativa.

| Nós ativos | Cluster funciona? |
| ---------- | ----------------- |
| 3          | ✅ Sim             |
| 2          | ✅ Sim             |
| 1          | ❌ Não             |

➡️ Por isso, **número ímpar de nós é obrigatório**.

***

## 🧠 Criar Exchanges e Quorum Queue no Cluster

### ✅ Exchange principal (Topic)

```bash
rabbitmqadmin declare exchange \
  name=topic_logs \
  type=topic \
  durable=true
```

***

### ✅ Dead Letter Exchange (DLX)

```bash
rabbitmqadmin declare exchange \
  name=dlx_logs \
  type=topic \
  durable=true
```

***

### ✅ Dead Letter Queue (DLQ)

```bash
rabbitmqadmin declare queue \
  name=dlq_logs \
  durable=true
```

***

### ✅ Binding DLX → DLQ

```bash
rabbitmqadmin declare binding \
  source=dlx_logs \
  destination=dlq_logs \
  destination_type=queue \
  routing_key="#"
```

***

### ✅ Criar **Quorum Queue**

```bash
rabbitmqadmin declare queue \
  name=teste-quorum \
  durable=true \
  arguments='{
    "x-queue-type": "quorum",
    "x-dead-letter-exchange": "dlx_logs",
    "x-dead-letter-routing-key": "NEW_Key",
    "x-delivery-limit": 5
  }'
```

✅ Replicação automática
✅ Leader election
✅ Failover sem perda
✅ Consistência forte

***

## 🔄 Fluxo Final do Sistema

    Producer
      ↓ (qualquer nó)
    topic_logs (Cluster Exchange)
      ↓
    teste-quorum (Replicada em 3 nós)
      ↓ basic_nack / delivery-limit
    dlx_logs (DLX)
      ↓
    dlq_logs (DLQ)

***

## 🧪 Teste de Failover

Pare um nó:

```bash
rabbitmqctl stop_app
```

Verifique liderança:

```bash
rabbitmqctl list_queues name leader replicas
```

✅ Outro nó assume automaticamente
✅ Aplicações não param

***

## ✅ Conclusão

Com este setup você possui:

✅ Cluster RabbitMQ com 3 nós
✅ Failover automático
✅ Zero perda de mensagens
✅ Quorum Queue em produção
✅ Código desacoplado da infra
