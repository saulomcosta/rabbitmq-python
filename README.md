# RabbitMQ + AMQP com Python (Pika)

## Estudos práticos de mensageria assíncrona — do básico ao avançado

Este repositório reúne **exemplos educacionais e práticos** sobre **mensageria assíncrona utilizando RabbitMQ**, o **protocolo AMQP (Advanced Message Queuing Protocol)** e a biblioteca **Pika em Python**.

O material foi organizado para **evoluir gradualmente**, abordando desde **conceitos fundamentais** (ACK, filas e exchanges) até **cenários avançados de produção**, como **Dead Letter Queue, RPC, Quorum Queues e Clusterização com failover automático**.

**Objetivo principal**  
> Servir como **guia de estudo, laboratório técnico e base conceitual** para quem deseja compreender **como o RabbitMQ funciona de verdade em sistemas distribuídos**.

## Conceitos Abordados no Repositório

Ao longo dos exemplos, são explorados:

✅ AMQP e RabbitMQ  
✅ Producer e Consumer  
✅ ACK automático vs ACK manual  
✅ Exchanges:

*   Fanout
*   Direct
*   Topic
*   Headers

✅ Routing Keys e Bindings  
✅ Dead Letter Exchange (DLX)  
✅ Dead Letter Queue (DLQ)  
✅ Rejeição e reentrega (`basic_nack`)  
✅ RPC sobre RabbitMQ (`reply_to`, `correlation_id`)  
✅ Criação manual de filas/exchanges via `rabbitmqadmin`  
✅ Quorum Queue  
✅ Cluster RabbitMQ (3 nós)  
✅ Failover automático e consistência forte (Raft)

## Estrutura do Repositório

    rabbitmq-amqp-python/
    ├── exemplo-ack/
    ├── exemplo-direct/
    ├── exemplo-fanout/
    ├── exemplo-topic/
    ├── exemplo-dlx/
    ├── exemplo-headers/
    ├── exemplo-replyTo/
    ├── exemplo-filas-exchange-binding/
    ├── exemplo-quorum/
    ├── exemplo-clusterizacao/
    └── README.md

Cada pasta é **independente**, possui **código funcional** e um **README próprio** explicando o conceito estudado.

## Descrição dos Exemplos

### `exemplo-ack`

**Foco:** ACK automático vs ACK manual

Explora:

*   `auto_ack=True` (rápido, porém arriscado)
*   `auto_ack=False` (confiável e recomendado)
*   Reentrega de mensagens em caso de falha

✅ Essencial para entender **confiabilidade**
✅ Base para qualquer projeto real com RabbitMQ

### `exemplo-direct`

**Foco:** Direct Exchange

Explora:

*   Roteamento **exato** por routing key
*   Logs por severidade
*   Bind seletivo entre filas e exchange

✅ Comum em sistemas de logs  
✅ Simples e eficiente

### `exemplo-fanout`

**Foco:** Fanout Exchange (Broadcast / Pub-Sub)

Explora:

*   Distribuição de mensagens para **todos**
*   Ausência de filtragem
*   Comunicação publish/subscribe

✅ Ideal para logs globais e eventos  
❌ Não indicado quando há necessidade de filtros

### `exemplo-topic`

**Foco:** Topic Exchange

Explora:

*   Routing keys hierárquicas
*   Uso de curingas `*` e `#`
*   Filtragem flexível por componente e severidade

✅ Um dos modelos mais usados em produção  
✅ Meio termo entre Direct e Headers

### `exemplo-dlx`

**Foco:** Dead Letter Exchange (DLX) + DLQ

Explora:

*   Rejeição de mensagens (`basic_nack`)
*   Envio automático para Dead Letter Queue
*   Tratamento de falhas e auditoria

✅ Essencial para sistemas resilientes  
✅ Muito usado em produção real

### `exemplo-headers`

**Foco:** Headers Exchange

Explora:

*   Roteamento baseado em **metadados**
*   Uso de headers AMQP
*   `x-match: any` vs `x-match: all`

✅ Muito flexível  
⚠️ Mais verboso que Topic/Direct

### `exemplo-replyTo`

**Foco:** RPC com RabbitMQ

Explora:

*   Comunicação Request / Response
*   Uso de `reply_to`
*   Uso de `correlation_id`
*   Fila exclusiva de callback

✅ Implementa o **RPC Pattern oficial do RabbitMQ**
✅ Útil quando HTTP não é ideal

### `exemplo-filas-exchange-binding`

**Foco:** Infraestrutura RabbitMQ via CLI

Explora:

*   Criação manual de exchanges
*   Criação de filas
*   Bindings explícitos
*   Quorum Queue
*   DLX + DLQ
*   Uso do `rabbitmqadmin`

✅ Ensina **infraestrutura separada do código**
✅ Simula ambientes reais de produção

### `exemplo-quorum`

**Foco:** Topic Exchange + Quorum Queue

Explora:

*   Quorum Queue
*   Delivery limit (`x-delivery-limit`)
*   Reentrega controlada
*   Integração com DLX/DLQ
*   Consistência forte

✅ Base para sistemas críticos  
✅ Pré-requisito para clusterização

### `exemplo-clusterizacao`

**Foco:** Cluster RabbitMQ com Quorum Queue

Explora:

*   Cluster com 3 nós
*   Uso de variáveis de ambiente:
    *   `RABBITMQ_NODENAME`
    *   `RABBITMQ_NODE_PORT`
    *   `RABBITMQ_SERVER_START_ARGS`
*   Failover automático
*   Eleição de líder
*   Alta disponibilidade real

✅ Cenário mais próximo de produção  
✅ Nenhuma perda de mensagens

## ▶️ Pré-requisitos Gerais

*   RabbitMQ
*   Erlang
*   Python 3.9+
*   Biblioteca Pika

```bash
pip install pika
```

*   Plugin `rabbitmq_management` habilitado

## Ordem Recomendada de Estudo

1️⃣ exemplo-ack  
2️⃣ exemplo-direct  
3️⃣ exemplo-fanout  
4️⃣ exemplo-topic  
5️⃣ exemplo-dlx  
6️⃣ exemplo-headers  
7️⃣ exemplo-replyTo  
8️⃣ exemplo-filas-exchange-binding  
9️⃣ exemplo-quorum  
🔟 exemplo-clusterizacao

Essa ordem reflete uma **evolução natural**, do básico ao avançado.

## Conclusão

Este repositório demonstra que:

> **RabbitMQ não é apenas filas. É um ecossistema completo para sistemas distribuídos.**
