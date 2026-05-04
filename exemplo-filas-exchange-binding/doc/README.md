## ✅ Pré-requisitos

*   RabbitMQ em execução
*   `rabbitmqadmin` disponível no sistema
    (normalmente em: `sbin/rabbitmqadmin`)

Se necessário, copie para `/usr/local/bin`:

```bash
sudo cp rabbitmqadmin /usr/local/bin/
sudo chmod +x /usr/local/bin/rabbitmqadmin
```

Teste:

```bash
rabbitmqadmin --help
```

***

# 🧱 1️⃣ Criar a Topic Exchange principal

### Exchange: `topic_logs`

```bash
rabbitmqadmin declare exchange \
  name=topic_logs \
  type=topic \
  durable=true
```

✅ Exchange usada pelo **Producer**
✅ Responsável pelo roteamento via routing keys

***

# ☠️ 2️⃣ Criar a Dead Letter Exchange (DLX)

### Exchange: `dlx_logs`

```bash
rabbitmqadmin declare exchange \
  name=dlx_logs \
  type=topic \
  durable=true
```

✅ Receberá mensagens rejeitadas ou que excederem o delivery limit

***

# 📥 3️⃣ Criar a Dead Letter Queue (DLQ)

### Queue: `dlq_logs`

```bash
rabbitmqadmin declare queue \
  name=dlq_logs \
  durable=true
```

✅ Armazenará mensagens rejeitadas
✅ Pode ser usada para auditoria ou reprocessamento

***

# 🔗 4️⃣ Binding DLX → DLQ

Binding com curinga `#` para receber **todas** as mensagens:

```bash
rabbitmqadmin declare binding \
  source=dlx_logs \
  destination=dlq_logs \
  destination_type=queue \
  routing_key="#"
```

***

# 🧠 5️⃣ Criar a **Quorum Queue**

### Queue: `teste-quorum`

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

### 🔎 O que cada argumento faz

| Argumento                   | Função                              |
| --------------------------- | ----------------------------------- |
| `x-queue-type=quorum`       | Define a fila como **Quorum Queue** |
| `durable=true`              | Fila persiste após restart          |
| `x-dead-letter-exchange`    | Exchange de mensagens rejeitadas    |
| `x-dead-letter-routing-key` | Routing key usada na DLX            |
| `x-delivery-limit=5`        | Máx. tentativas antes da DLQ        |

✅ Replicação automática
✅ Um líder + seguidores
✅ Consistência forte (Raft)

***

# 🔗 6️⃣ Binding Topic Exchange → Quorum Queue

### Exemplo 1 – Todas mensagens do componente `A`

```bash
rabbitmqadmin declare binding \
  source=topic_logs \
  destination=teste-quorum \
  destination_type=queue \
  routing_key="A.*"
```

### Exemplo 2 – Todas mensagens de erro

```bash
rabbitmqadmin declare binding \
  source=topic_logs \
  destination=teste-quorum \
  destination_type=queue \
  routing_key="*.error"
```

### Exemplo 3 – Receber tudo

```bash
rabbitmqadmin declare binding \
  source=topic_logs \
  destination=teste-quorum \
  destination_type=queue \
  routing_key="#"
```

✅ Os bindings substituem os parâmetros passados via CLI no Consumer
✅ Totalmente compatível com o script Python

***

# 🧪 7️⃣ Fluxo Final do Sistema

    Producer
       ↓
    topic_logs (Topic Exchange)
       ↓
    teste-quorum (Quorum Queue)
       ↓ basic_nack / delivery-limit
    dlx_logs (DLX)
       ↓
    dlq_logs (DLQ)

***

# ✅ Validação rápida

Listar filas:

```bash
rabbitmqadmin list queues name queue_type messages
```

Listar exchanges:

```bash
rabbitmqadmin list exchanges name type
```

Listar bindings:

```bash
rabbitmqadmin list bindings
```

***

# ✅ Conclusão

Com esses comandos, você:

✅ Criou **infraestrutura RabbitMQ manualmente**
✅ Separou **infra (broker)** de **código (Python)**
✅ Usou **Quorum Queue** corretamente
✅ Implementou **reentrega controlada + DLQ**
✅ Simulou um cenário **real de produção**

