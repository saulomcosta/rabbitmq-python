# 📂 Pasta `exemplo-dlx`

## 📌 Visão Geral

A pasta **`exemplo-dlx`** contém exemplos educacionais e práticos que demonstram o uso de **Topic Exchange** no RabbitMQ, utilizando o **protocolo AMQP (Advanced Message Queuing Protocol)** e a biblioteca **Pika em Python**.

Este exemplo vai além do roteamento básico e demonstra também:

*   ✅ **Topic Exchange**
*   ✅ **Routing keys hierárquicas**
*   ✅ **Curingas `*` e `#`**
*   ✅ **Fila temporária e exclusiva**
*   ✅ **Dead Letter Exchange (DLX)**
*   ✅ **Dead Letter Queue (DLQ)**
*   ✅ **Rejeição de mensagens com `basic_nack`**

É um cenário ideal para estudo de **fluxo de falhas**, **tratamento de erros** e **observabilidade em sistemas assíncronos**.

***

## 🧱 Estrutura dos Arquivos

    exemplo-dlx/
    ├── producer_topic.py
    ├── consumer_topic.py
    └── doc/README.md

***

## 📜 Descrição dos Arquivos

## 🔹 `producer_topic.py`

### ✅ O que é

Script responsável por **produzir (enviar)** mensagens para o RabbitMQ utilizando uma **Topic Exchange**.

### ✅ O que ele faz

*   Conecta-se a um broker RabbitMQ local
*   Autentica-se com credenciais explícitas (`guest/guest`)
*   Declara a exchange `topic_logs` do tipo **TOPIC**
*   Monta **routing keys hierárquicas**
*   Publica mensagens sequenciais
*   Insere pausa entre os envios para facilitar a observação

### ✅ Formato das routing keys

As mensagens são publicadas no formato:

    <componente>.<severidade>

### ✅ Exemplos gerados pelo Producer

```text
A.info
B.error
A.warning
A.error
B.info
```

### ✅ Exemplo de envio no terminal

```text
[x] Enviado:'A.info' - A
[x] Enviado:'B.error' - B
```

***

## 🔹 `consumer_topic.py`

### ✅ O que é

Script responsável por **consumir (receber)** mensagens publicadas na Topic Exchange, aplicando **filtros por padrões de routing key** e **forçando falha para envio à DLQ**.

### ✅ O que ele faz

*   Conecta-se ao RabbitMQ local
*   Autentica-se com credenciais explícitas (`guest/guest`)
*   Declara a exchange `topic_logs`
*   Declara uma **Dead Letter Exchange (`dlx_logs`)**
*   Declara uma **Dead Letter Queue (`dlq_logs`)**
*   Cria uma **fila temporária e exclusiva**
*   Associa a fila a uma **DLX**
*   Realiza o bind com padrões informados via CLI
*   Consome mensagens com **ACK manual**
*   **Rejeita explicitamente todas as mensagens (`basic_nack`)**

### ✅ Rejeição e Dead Letter

Toda mensagem consumida é rejeitada:

```python
channel.basic_nack(
    delivery_tag=method.delivery_tag,
    requeue=False
)
```

Como a fila possui uma **Dead Letter Exchange configurada**, as mensagens rejeitadas são automaticamente encaminhadas para:

*   **Dead Letter Exchange:** `dlx_logs`
*   **Dead Letter Queue:** `dlq_logs`

***

## ⚙️ Configuração da Dead Letter Queue (DLQ)

### 🧠 Arquitetura aplicada

    Producer
       ↓
    topic_logs (Topic Exchange)
       ↓
    Fila Temporária (Consumer)
       ↓ basic_nack
    dlx_logs (DLX)
       ↓
    dlq_logs (DLQ)

### ✅ Objetivo da DLQ

*   Auditoria de falhas
*   Simulação de erro de processamento
*   Retenção de mensagens rejeitadas
*   Testes de resiliência

***

## ▶️ Uso de Argumentos na Execução (Bindings)

Os **bindings são passados via linha de comando**.

### ✅ Exemplo de execução

```bash
python consumer_topic.py "A.*" "*.error"
```

### ✅ Nesse cenário, o Consumer receberá:

*   Todas as mensagens do componente `A`
*   Todas as mensagens com severidade `error`

***

## 🔄 Fluxo de Funcionamento (Topic + DLX)

1.  O **Producer** envia mensagens para `topic_logs`
2.  Cada mensagem possui uma **routing key hierárquica**
3.  O RabbitMQ compara a routing key com os **bindings**
4.  A mensagem é entregue à fila temporária
5.  O Consumer **processa e rejeita a mensagem**
6.  A mensagem é redirecionada para a **DLX**
7.  A DLX encaminha a mensagem para a **DLQ**

***

## 🎯 Curingas em Topic Exchange

| Curinga | Significado                         |
| ------- | ----------------------------------- |
| `*`     | Substitui **uma única palavra**     |
| `#`     | Substitui **zero ou mais palavras** |

### ✅ Exemplos práticos

| Binding   | Mensagens recebidas      |
| --------- | ------------------------ |
| `A.*`     | `A.info`, `A.error`      |
| `*.error` | `A.error`, `B.error`     |
| `#`       | Todas as mensagens       |
| `A.#`     | Tudo que começa com `A.` |

***

## 🛠️ Como Executar os Exemplos

### ✅ Pré-requisitos

*   RabbitMQ em execução localmente
*   Python 3.9 ou superior
*   Biblioteca Pika instalada

```bash
pip install pika
```

Credenciais utilizadas:

*   **Usuário:** `guest`
*   **Senha:** `guest`

***

### ✅ Passo a Passo

#### 1️⃣ Execute o Consumer

```bash
python consumer_topic.py "A.*" "*.error"
```

O Consumer ficará em escuta contínua.

***

#### 2️⃣ Execute o Producer

```bash
python producer_topic.py
```

***

## ✅ Resultado Esperado

*   O Consumer recebe apenas mensagens compatíveis com os bindings
*   Todas as mensagens são **rejeitadas**
*   Mensagens rejeitadas são armazenadas na **DLQ**
*   Possibilidade de inspeção posterior das falhas
*   Consumidores adicionais podem usar outros filtros

***

## 📊 Quando Usar Topic Exchange + DLQ

Esse padrão é indicado quando:

*   O roteamento precisa ser flexível
*   Há necessidade de **tratamento de falhas**
*   Sistemas exigem **auditabilidade**
*   Processamento é assíncrono e resiliente

### Exemplos reais

*   Logs distribuídos
*   Monitoramento de serviços
*   Pipelines de eventos
*   Arquiteturas orientadas a falhas

***

## 🔎 Comparação com Outros Tipos de Exchange

| Exchange | Roteamento | Uso comum         |
| -------- | ---------- | ----------------- |
| Fanout   | Broadcast  | Logs globais      |
| Direct   | Exato      | Severidade        |
| Topic    | Padrões    | Módulo + tipo     |
| Headers  | Headers    | Filtros avançados |

***

## ✅ Conclusão

A pasta **`exemplo-dlx`** demonstra um cenário completo e realista de mensageria com RabbitMQ, abordando:

✅ Topic Exchange
✅ Routing Keys avançadas
✅ Filas temporárias
✅ Dead Letter Exchange
✅ Dead Letter Queue
✅ Rejeição controlada de mensagens
