# 📂 Pasta `exemplo-topic`

## 📌 Visão Geral

A pasta **`exemplo-topic`** contém exemplos educacionais e práticos que demonstram o uso de **Topic Exchange** no RabbitMQ, utilizando o **protocolo AMQP (Advanced Message Queuing Protocol)** e a biblioteca **Pika em Python**.

O objetivo principal deste exemplo é demonstrar o **roteamento flexível e hierárquico de mensagens**, onde o destino das mensagens é definido por **padrões de routing key**, permitindo o uso de **curingas (`*` e `#`)**.

Esse modelo é muito utilizado em:

*   Sistemas de logs distribuídos
*   Monitoramento por módulo e severidade
*   Arquiteturas orientadas a eventos
*   Processamento seletivo de mensagens

***

## 🧱 Estrutura dos Arquivos

    exemplo-topic/
    ├── producer_topic.py
    ├── consumer_topic.py
    └── README.md

***

## 📜 Descrição dos Arquivos

### 🔹 `producer_topic.py`

### O que é

Script responsável por **produzir (enviar)** mensagens para o RabbitMQ utilizando uma **Topic Exchange**.

### O que ele faz

*   Conecta-se a um broker RabbitMQ local
*   Autentica-se com credenciais explícitas (`admin/admin`)
*   Declara a exchange `topic_logs` do tipo **TOPIC**
*   Monta routing keys combinando **componente** e **severidade**
*   Publica mensagens sequenciais na exchange
*   Envia mensagens com pausa entre os envios

### Exemplo de routing keys geradas

```text
A.info
B.error
A.warning
A.error
B.info
```

Cada mensagem enviada possui uma routing key no formato:

    <componente>.<severidade>

***

### 🔹 `consumer_topic.py`

### O que é

Script responsável por **consumir (receber)** mensagens publicadas na Topic Exchange, filtrando-as por **padrões de routing key**.

### O que ele faz

*   Conecta-se ao RabbitMQ local
*   Autentica-se com usuário e senha explícitos
*   Declara a exchange `topic_logs`
*   Cria uma **fila temporária e exclusiva**
*   Realiza o **bind da fila com padrões de routing key**
*   Permanece em escuta contínua aguardando mensagens
*   Processa mensagens com **ACK automático**

### Uso de argumentos na execução

O Consumer recebe os **bindings** via linha de comando:

```bash
python consumer_topic.py "A.*" "*.error"
```

Nesse exemplo, o Consumer receberá:

*   Todas as mensagens do componente `A`
*   Todas as mensagens com severidade `error`

***

## 🔄 Fluxo de Funcionamento (Topic Exchange)

1.  O **Producer** envia mensagens para a exchange `topic_logs`
2.  Cada mensagem possui uma **routing key hierárquica**
3.  O RabbitMQ compara a routing key da mensagem com os **bindings da fila**
4.  Se a routing key **corresponder ao padrão**, a mensagem é entregue
5.  O **Consumer** recebe e processa a mensagem

***

## 🎯 Curiosidades sobre Topic Exchange

### Curingas disponíveis

| Curinga | Significado                         |
| ------- | ----------------------------------- |
| `*`     | Substitui **uma única palavra**     |
| `#`     | Substitui **zero ou mais palavras** |

### Exemplos de Binding

| Binding   | Mensagens recebidas            |
| --------- | ------------------------------ |
| `A.*`     | `A.info`, `A.error`, `A.debug` |
| `*.error` | `A.error`, `B.error`           |
| `#`       | Todas as mensagens             |
| `A.#`     | Tudo que começa com `A.`       |

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

Em um terminal, informe os padrões desejados:

```bash
python consumer_topic.py "A.*" "*.error"
```

O Consumer ficará aguardando mensagens compatíveis com esses padrões.

***

#### 2️⃣ Execute o Producer

Em outro terminal:

```bash
python producer_topic.py
```

***

### ✅ Resultado esperado

*   O Consumer receberá **apenas as mensagens** que correspondam aos bindings informados
*   Mensagens que não correspondam **não serão entregues**
*   Outros consumers podem usar bindings diferentes simultaneamente

***

## 📊 Quando Usar Topic Exchange

A **Topic Exchange** é indicada quando:

*   O roteamento precisa ser **flexível**
*   As mensagens possuem **estrutura hierárquica**
*   É necessário filtrar por múltiplos critérios
*   Direct Exchange é limitado demais

### Exemplos reais de uso

*   Logs por módulo e severidade
*   Monitoramento distribuído
*   Microserviços orientados a eventos
*   Sistemas de auditoria

***

## 🔎 Comparação com Outros Tipos de Exchange

| Exchange | Roteamento   | Uso comum           |
| -------- | ------------ | ------------------- |
| Fanout   | Broadcast    | Logs globais        |
| Direct   | Exato        | Severidade          |
| Topic    | Padrões      | Módulo + severidade |
| Headers  | Headers AMQP | Filtros complexos   |

***

## ✅ Conclusão

A pasta **`exemplo-topic`** demonstra um dos modelos mais utilizados e poderosos do RabbitMQ, oferecendo:

*   ✅ Flexibilidade
*   ✅ Escalabilidade
*   ✅ Controle refinado sobre o consumo
*   ✅ Alto nível de reutilização

É o meio termo ideal entre **simplicidade (Direct)** e **complexidade (Headers)**.

