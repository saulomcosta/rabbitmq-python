# 📘 Exemplo RPC com RabbitMQ (`reply_to` + `correlation_id`)

## 📌 Visão Geral

Este projeto demonstra, de forma **educacional e prática**, como implementar **RPC (Remote Procedure Call)** utilizando **RabbitMQ**, o protocolo **AMQP (Advanced Message Queuing Protocol)** e a biblioteca **Pika em Python**.

O padrão RPC simula uma chamada de função remota, porém baseada em **mensageria assíncrona**, desacoplando totalmente o **Producer (Sender)** do **Consumer (Receiver)**.

***

## 🎯 Objetivo do Exemplo

Demonstrar:

*   Como um **Producer** envia uma requisição RPC
*   Como um **Consumer** processa essa requisição
*   Como o retorno ocorre usando:
    *   `reply_to`
    *   `correlation_id`
*   Como o Producer aguarda a resposta correta
*   Como o RabbitMQ atua apenas como **intermediário**

***

## 🧱 Arquitetura Geral

### Componentes envolvidos

| Componente             | Responsabilidade                                   |
| ---------------------- | -------------------------------------------------- |
| Producer (Sender)      | Envia a requisição RPC e aguarda a resposta        |
| Consumer (Receiver)    | Processa a requisição e devolve a resposta         |
| RabbitMQ               | Broker de mensagens (intermedia envio e resposta)  |
| Fila RPC (`rpc.queue`) | Recebe requisições                                 |
| Fila de Callback       | Fila exclusiva criada pelo Producer para respostas |

***

## 🔑 Conceitos Fundamentais

### 🔹 `reply_to`

*   Propriedade AMQP que indica **para qual fila a resposta deve ser enviada**
*   No RPC, o Producer cria uma **fila temporária exclusiva**
*   O Consumer **não sabe quem é o Producer**, apenas responde para `reply_to`

### 🔹 `correlation_id`

*   Identificador único (UUID)
*   Permite ao Producer **associar uma resposta à requisição correta**
*   Essencial quando várias chamadas RPC ocorrem simultaneamente

***

## 🔄 Fluxo Completo do RPC (Passo a Passo)

### 1️⃣ Inicialização do Consumer

*   Conecta ao RabbitMQ
*   Declara a fila `rpc.queue`
*   Fica em escuta usando `start_consuming()`

### 2️⃣ Inicialização do Producer

*   Conecta ao RabbitMQ
*   Cria uma **fila exclusiva e temporária** (callback)
*   Registra um consumer para essa fila de resposta

### 3️⃣ Envio da Requisição

O Producer:

*   Gera um `correlation_id`
*   Publica a mensagem na fila `rpc.queue`
*   Define:
    *   `reply_to` → fila de callback
    *   `correlation_id` → UUID gerado

### 4️⃣ Processamento no Consumer

O Consumer:

*   Recebe a mensagem
*   Processa o dado (ex: `30 * 30`)
*   Publica a resposta na fila indicada em `reply_to`
*   Mantém o mesmo `correlation_id`

### 5️⃣ Recebimento da Resposta

O Producer:

*   Recebe mensagens na fila de callback
*   Verifica se o `correlation_id` recebido é o esperado
*   Consome a resposta correta
*   Interrompe o consumo

***

## 🧩 Diagrama Explicativo (Fluxo RPC)

```text
 ┌────────────┐                ┌──────────────┐
 │  Producer  │                │   Consumer   │
 │  (Sender)  │                │  (Receiver)  │
 └─────┬──────┘                └──────┬───────┘
       │                                   │
       │ 1. Cria fila callback exclusiva   │
       │                                   │
       │ 2. Envia mensagem RPC             │
       │ ───────────────────────────────▶ │
       │    queue: rpc.queue               │
       │    correlation_id: UUID           │
       │    reply_to: callback_queue       │
       │                                   │
       │                                   │ 3. Processa requisição
       │                                   │    (ex: 30 * 30)
       │                                   │
       │ 4. Envia resposta                 │
       │ ◀─────────────────────────────── │
       │    queue: callback_queue          │
       │    correlation_id: UUID           │
       │                                   │
       │ 5. Valida correlation_id          │
       │    Consome resposta correta       │
       │                                   │
```

***

## 📂 Estrutura dos Arquivos

```text
.
├── sender.py      # Producer RPC
├── receiver.py    # Consumer RPC
└── README.md
```

***

## ▶️ Como Executar o Projeto

### ✅ Pré-requisitos

*   Python 3.9+
*   RabbitMQ em execução (local)
*   Biblioteca Pika instalada:

```bash
pip install pika
```

> Certifique-se de que o RabbitMQ esteja rodando em `localhost`
> com usuário e senha `admin / admin`

***

### ✅ Passo 1 — Inicie o Consumer

Em um terminal:

```bash
python receiver.py
```

Saída esperada:

```text
[x] Aguardando requisições RPC...
```

***

### ✅ Passo 2 — Execute o Producer

Em outro terminal:

```bash
python sender.py
```

Saída esperada no Producer:

```text
[x] Aguardando resposta na fila: amq.gen-XXXX
[→] Requisição enviada (correlation_id=...)
[✓] Resposta recebida: 900
```

Saída esperada no Consumer:

```text
[*] Processando: 30 * 30
[✓] Resposta enviada
```

***

## 🛑 Comportamento Importante

*   O **Consumer permanece ativo** indefinidamente
*   O **Producer encerra automaticamente** após receber a resposta
*   Caso não exista Consumer ativo:
    *   A fila acumula mensagens
    *   O Producer ficará aguardando indefinidamente (sem timeout)

***

## ✅ Boas Práticas Demonstradas

*   Uso correto de `reply_to` e `correlation_id`
*   Fila exclusiva de callback (`queue=""`)
*   `basic_ack` no Consumer
*   Encerramento explícito de conexão
*   Ponto de entrada com `if __name__ == "__main__"`

***

## 🚀 Possíveis Evoluções

*   Adicionar **timeout no Producer**
*   Implementar **múltiplas chamadas RPC**
*   Criar **tratamento de erro**
*   Migrar para **SelectConnection / asyncio**
*   Usar **Direct ou Topic Exchange**

***

## 📚 Referência Conceitual

Este padrão é baseado no **RPC Pattern oficial do RabbitMQ**, amplamente utilizado quando:

*   HTTP não é ideal
*   É necessário desacoplamento
*   Processamentos são distribuídos

***

## ✍️ Autor

**Saulo Costa**
Exemplo educacional para estudo de mensageria, RPC e RabbitMQ.

