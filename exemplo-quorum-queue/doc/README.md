# 📂 Topic Exchange com **Quorum Queue**

## 📌 Visão Geral

Este exemplo demonstra o uso de **Quorum Queues** no RabbitMQ em conjunto com uma **Topic Exchange**, utilizando o **protocolo AMQP (Advanced Message Queuing Protocol)** e a biblioteca **Pika em Python**.

O objetivo é apresentar um cenário **robusto e realista de mensageria**, abordando não apenas o roteamento flexível de mensagens, mas também **alta disponibilidade**, **consistência forte** e **tratamento de falhas**, características centrais das *Quorum Queues*.

O exemplo é composto por dois scripts:

*   **Producer** – responsável por publicar mensagens
*   **Consumer** – responsável por consumir mensagens a partir de uma **fila quorum**, com controle de falhas e Dead Letter Queue

***

## 🧱 Estrutura dos Arquivos

    exemplo-quorum-topic/
    ├── producer_topic.py
    ├── consumer_topic_quorum.py
    └── README.md

***

## ⚙️ Tecnologias e Conceitos Utilizados

*   RabbitMQ
*   AMQP
*   Pika (Python)
*   Topic Exchange
*   Quorum Queue
*   Routing Keys hierárquicas
*   Curingas `*` e `#`
*   Dead Letter Exchange (DLX)
*   Dead Letter Queue (DLQ)
*   Controle manual de ACK / NACK
*   Delivery Limit (`x-delivery-limit`)

***

## 📨 `producer_topic.py`

### ✅ O que é

Script responsável por **produzir (enviar)** mensagens para o RabbitMQ através de uma **Topic Exchange**.

### ✅ Papel do Producer em Quorum Queues

O Producer **não declara filas** e **não precisa conhecer o tipo da fila**.
Isso é um ponto-chave da arquitetura:

> ✅ O Producer publica mensagens na exchange
> ✅ O RabbitMQ entrega essas mensagens a filas **quorum** ou **classic**, conforme configurado no Consumer

Esse desacoplamento permite alta flexibilidade e evolução da arquitetura sem impacto no Producer.

### ✅ O que o Producer faz

*   Conecta-se ao RabbitMQ local
*   Autentica-se com credenciais explícitas
*   Declara a exchange `topic_logs` do tipo **TOPIC**
*   Cria routing keys no formato:

<!---->

    <componente>.<severidade>

*   Publica mensagens sequenciais com intervalo entre envios

### ✅ Exemplos de routing keys geradas

```text
A.info
B.error
A.warning
A.error
B.info
```

***

## 📥 `consumer_topic_quorum.py`

### ✅ O que é

Script responsável por **consumir mensagens** a partir de uma **Quorum Queue**, demonstrando controle de falhas, reentregas e envio automático para **Dead Letter Queue**.

### ✅ O que é uma Quorum Queue

A **Quorum Queue** é um tipo de fila introduzido pelo RabbitMQ para cenários que exigem:

*   ✅ Alta disponibilidade
*   ✅ Replicação entre nós do cluster
*   ✅ Consistência forte (baseada em Raft)
*   ✅ Tolerância a falhas de nó
*   ✅ Eliminação de problemas comuns das filas classic HA

Cada Quorum Queue possui:

*   Um **líder**
*   Um conjunto de **followers**
*   Replicação síncrona das mensagens

***

### ✅ O que o Consumer faz

*   Conecta-se ao RabbitMQ
*   Declara a exchange `topic_logs` (TOPIC)
*   Declara uma **Dead Letter Exchange (`dlx_logs`)**
*   Declara uma **Dead Letter Queue (`dlq_logs`)**
*   Declara uma **Quorum Queue durável**
*   Configura:
    *   `x-queue-type: quorum`
    *   `x-delivery-limit`
    *   DLX e routing key de dead letter
*   Faz o bind da fila usando padrões informados via CLI
*   Consome mensagens com **ACK manual**
*   Rejeita mensagens com `basic_nack`

***

### ⚠️ Rejeição, Reentrega e Delivery Limit

O Consumer **rejeita mensagens** usando:

```python
basic_nack(requeue=True)
```

Em Quorum Queues:

*   Cada rejeição incrementa o contador interno de entregas
*   Esse contador é controlado por:

```text
x-delivery-limit
```

Quando o limite é atingido:

✅ A mensagem **não é mais reentregue**
✅ É automaticamente enviada para a **Dead Letter Exchange**
✅ Fica disponível para auditoria na **Dead Letter Queue**

***

## ☠️ Dead Letter Exchange e Dead Letter Queue

### Arquitetura aplicada

    Producer
       ↓
    Topic Exchange (topic_logs)
       ↓
    Quorum Queue (teste-quorum)
       ↓ basic_nack / delivery-limit
    Dead Letter Exchange (dlx_logs)
       ↓
    Dead Letter Queue (dlq_logs)

### Objetivos da DLQ

*   Análise de falhas
*   Auditoria de mensagens problemáticas
*   Simulação de erros de consumo
*   Observabilidade do sistema

***

## ▶️ Execução dos Scripts

### ✅ Pré-requisitos

*   RabbitMQ em execução (local ou cluster)
*   Python 3.9+
*   Biblioteca Pika instalada

```bash
pip install pika
```

Credenciais utilizadas no exemplo:

*   Usuário: `guest`
*   Senha: `guest`

***

### ✅ Passo 1 – Executar o Consumer (Quorum Queue)

```bash
python consumer_topic_quorum.py "A.*" "*.error"
```

O Consumer ficará aguardando mensagens compatíveis com os padrões informados.

***

### ✅ Passo 2 – Executar o Producer

```bash
python producer_topic.py
```

***

## ✅ Resultado Esperado

*   As mensagens são roteadas via Topic Exchange
*   Apenas mensagens compatíveis com os bindings são entregues
*   O Consumer rejeita mensagens propositalmente
*   O RabbitMQ controla o número de reentregas
*   Mensagens que excedem o limite são enviadas para a DLQ
*   Nenhuma mensagem é perdida

***

## 📊 Quando Usar Quorum Queue

Use **Quorum Queues** quando:

✅ O sistema exige alta disponibilidade
✅ Não pode haver perda de mensagens
✅ Há múltiplos nós RabbitMQ
✅ Consistência é mais importante que latência mínima

### Exemplos de uso real

*   Sistemas financeiros
*   Eventos críticos
*   Processamento assíncrono resiliente
*   Logs e auditoria
*   Microserviços orientados a eventos

***

## 🔎 Classic Queue × Quorum Queue

| Característica      | Classic       | Quorum |
| ------------------- | ------------- | ------ |
| Replicação          | Opcional (HA) | Nativa |
| Consistência        | Eventual      | Forte  |
| Tolerância a falhas | Média         | Alta   |
| Leader              | Não explícito | Sim    |
| Tecnologia          | Espelhamento  | Raft   |

***

## ✅ Conclusão

Este exemplo demonstra um **pipeline completo de mensageria moderna**, combinando:

✅ Topic Exchange
✅ Routing Keys flexíveis
✅ Quorum Queue
✅ Controle de falhas
✅ Reentrega limitada
✅ Dead Letter Queue

