# 📂 Pasta `exemplo-fanout`

## 📌 Visão Geral

A pasta **`exemplo-fanout`** contém exemplos educacionais e práticos que demonstram o uso de **Fanout Exchange** no RabbitMQ, utilizando o **protocolo AMQP (Advanced Message Queuing Protocol)** e a biblioteca **Pika em Python**.

O objetivo principal deste exemplo é demonstrar o conceito de **broadcast de mensagens**, onde **todas as filas vinculadas a uma exchange recebem a mesma mensagem**, independentemente de routing keys.

Esse padrão é amplamente utilizado em:

*   Sistemas de logs
*   Eventos de sistema
*   Notificações globais
*   Comunicação publish/subscribe (pub/sub)

***

## 🧱 Estrutura dos Arquivos

    exemplo-fanout/
    ├── producer_fanout.py
    ├── consumer_fanout.py
    └── README.md

***

## 📜 Descrição dos Arquivos

### 🔹 `producer_fanout.py`

### O que é

Script responsável por **produzir (enviar)** mensagens para o RabbitMQ utilizando uma **Fanout Exchange**.

### O que ele faz

*   Conecta-se a um broker RabbitMQ local
*   Autentica-se com credenciais explícitas (`admin/admin`)
*   Declara a exchange `logs` do tipo **FANOUT**
*   Publica mensagens sequenciais na exchange
*   Não utiliza routing keys (ignoradas por fanout)
*   Envia mensagens com pausa entre os envios

### Conceitos demonstrados

*   Producer RabbitMQ
*   Declaração de `exchange_type="fanout"`
*   Publicação via exchange (não diretamente em filas)
*   Padrão **broadcast**

📌 **Importante:**
Em uma Fanout Exchange, **todas as filas vinculadas recebem todas as mensagens**, sem qualquer filtragem.

***

### 🔹 `consumer_fanout.py`

### O que é

Consumer implementado em formato de **classe**, responsável por **receber e processar mensagens** enviadas pelo Producer via Fanout Exchange.

### O que ele faz

*   Conecta-se ao RabbitMQ local
*   Autentica-se com usuário e senha explícitos
*   Declara a mesma exchange `logs` do tipo **FANOUT**
*   Declara uma fila chamada `hello`
*   Realiza o **bind da fila com a exchange**
*   Entra em escuta contínua aguardando mensagens
*   Processa mensagens automaticamente (`auto_ack=True`)

### Conceitos demonstrados

*   Consumer RabbitMQ
*   Uso de Fanout Exchange
*   Bind entre fila e exchange
*   Encapsulamento da lógica em classe
*   ACK automático

📌 **Destaque:**
Qualquer número de consumers pode ser iniciado, e **todos receberão as mesmas mensagens**, desde que possuam filas vinculadas à exchange.

***

## 🔄 Fluxo de Funcionamento (Fanout Exchange)

1.  O **Producer** envia mensagens para a exchange `logs`
2.  A exchange do tipo **fanout** replica a mensagem
3.  Todas as filas vinculadas recebem uma cópia
4.  Cada **Consumer** processa a mensagem de forma independente

📊 **Não há roteamento ou filtragem** neste modelo.

***

## ▶️ Como Executar os Exemplos

### ✅ Pré-requisitos

*   RabbitMQ em execução localmente
*   Python 3.9 ou superior
*   Biblioteca Pika instalada

Instalação do Pika:

```bash
pip install pika
```

Usuário configurado no RabbitMQ:

*   **Usuário:** `admin`
*   **Senha:** `admin`

***

### ✅ Passo a Passo de Execução

#### 1️⃣ Execute o Consumer

Em um terminal:

```bash
python consumer_fanout.py
```

O Consumer ficará aguardando mensagens publicadas na exchange `logs`.

***

#### 2️⃣ Execute o Producer

Em outro terminal:

```bash
python producer_fanout.py
```

O Producer começará a publicar mensagens sequenciais.

***

### ✅ Resultado esperado

*   Todas as mensagens enviadas pelo Producer
*   Serão recebidas pelo Consumer
*   Se outro Consumer for iniciado, ele também receberá todas as mensagens futuras

***

## 📊 Quando Usar Fanout Exchange

A **Fanout Exchange** é indicada quando:

*   Você precisa **distribuir mensagens para todos**
*   Não há necessidade de filtragem
*   O foco é **broadcast**
*   O mesmo evento deve ser processado por múltiplos serviços

### Exemplos reais

*   Logs distribuídos
*   Eventos de monitoramento
*   Sistemas de notificação
*   Arquitetura publish/subscribe

***

## ✅ Conclusão

A pasta **`exemplo-fanout`** demonstra de forma clara e prática como o RabbitMQ implementa comunicação **pub/sub**, permitindo que um evento seja entregue a múltiplos consumidores simultaneamente.

Este padrão:

*   ✅ É simples
*   ✅ Altamente escalável
*   ✅ Ideal para disseminação de eventos
*   ❌ Não permite filtragem de mensagens

***

## 🔎 Comparação Rápida

| Tipo de Exchange | Roteamento           | Uso principal         |
| ---------------- | -------------------- | --------------------- |
| Fanout           | Broadcast (todos)    | Logs, eventos globais |
| Direct           | Exato (routing\_key) | Logs por severidade   |
| Topic            | Padrões e curingas   | Logs por módulo       |
| Headers          | Headers AMQP         | Filtros complexos     |
