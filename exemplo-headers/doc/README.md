# 📂 Pasta `exemplo-headers`

## 📌 Visão Geral

A pasta **`exemplo-headers`** contém exemplos educacionais e práticos que demonstram o uso de **Headers Exchange** no RabbitMQ, utilizando o **protocolo AMQP (Advanced Message Queuing Protocol)** e a biblioteca **Pika em Python**.

O objetivo principal deste exemplo é demonstrar um modelo de **roteamento avançado de mensagens**, onde o destino das mensagens é decidido com base em **headers (pares chave/valor)**, e não por routing keys.

Esse modelo é ideal quando o roteamento depende de **múltiplos atributos simultaneamente**, como:

*   Componente da aplicação
*   Severidade
*   Ambiente
*   Tipo de evento

***

## 🧱 Estrutura dos Arquivos

    exemplo-headers/
    ├── producer_headers.py
    ├── consumer_headers.py
    └── README.md

***

## 📜 Descrição dos Arquivos

### 🔹 `producer_headers.py`

### O que é

Script responsável por **produzir (enviar)** mensagens para o RabbitMQ utilizando uma **Headers Exchange**.

### O que ele faz

*   Conecta-se a um broker RabbitMQ local
*   Autentica-se com credenciais explícitas (`admin/admin`)
*   Declara a exchange `headers_logs` do tipo **HEADERS**
*   Publica mensagens contendo **headers personalizados**
*   Não utiliza routing keys (ignoradas em exchanges HEADERS)
*   Envia mensagens sequenciais com pausa entre os envios

### Headers utilizados nas mensagens

Cada mensagem é enviada com headers semelhantes a:

```json
{
  "components": "A",
  "severities": "info"
}
```

Esses headers são utilizados pelo RabbitMQ para decidir **quais filas receberão a mensagem**.

***

### 🔹 `consumer_headers.py`

### O que é

Script responsável por **consumir (receber)** mensagens publicadas na Headers Exchange, filtrando-as com base em **critérios definidos nos headers**.

### O que ele faz

*   Conecta-se ao RabbitMQ local
*   Autentica-se com usuário e senha explícitos
*   Declara a exchange `headers_logs`
*   Cria uma **fila temporária e exclusiva**
*   Realiza o **bind da fila com headers específicos**
*   Permanece em escuta contínua aguardando mensagens
*   Processa mensagens automaticamente (`auto_ack=True`)

### Bind por headers

O bind da fila utiliza o parâmetro `arguments`, por exemplo:

```python
headers = {
    "components": "API",
    "severities": "error",
    "x-match": "any"
}
```

📌 **Importante:**
O campo `x-match` define o comportamento do roteamento:

*   `any` → a mensagem é roteada se **qualquer** header coincidir
*   `all` → a mensagem só é roteada se **todos** os headers coincidirem

***

## 🔄 Fluxo de Funcionamento (Headers Exchange)

1.  O **Producer** envia mensagens para a exchange `headers_logs`
2.  Cada mensagem contém **headers personalizados**
3.  O RabbitMQ compara os headers da mensagem com os headers definidos no bind
4.  Se os critérios forem atendidos (`any` ou `all`), a mensagem é entregue à fila
5.  O **Consumer** processa a mensagem

📌 **Não existe routing key nesse modelo**.

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

Em um terminal, informe os headers esperados:

```bash
python consumer_headers.py A info
```

Esse consumer aguardará mensagens que contenham:

*   `components = A`
*   `severities = info`

***

#### 2️⃣ Execute o Producer

Em outro terminal:

```bash
python producer_headers.py
```

O Producer enviará mensagens com diferentes combinações de headers.

***

### ✅ Resultado esperado

*   O Consumer receberá **somente as mensagens** cujos headers coincidirem com os definidos no bind
*   Mensagens com headers diferentes **não serão entregues**

***

## 📊 Quando Usar Headers Exchange

A **Headers Exchange** é indicada quando:

*   O roteamento depende de **múltiplos atributos**
*   Routing key única não é suficiente
*   É necessário aplicar **lógica mais rica de filtragem**
*   O sistema exige flexibilidade no direcionamento

### Exemplos reais

*   Logs corporativos complexos
*   Eventos com múltiplos critérios
*   Mensageria baseada em metadados
*   Sistemas distribuídos com regras dinâmicas

***

## 🔎 Comparação com Outros Tipos de Exchange

| Exchange | Roteamento   | Uso típico          |
| -------- | ------------ | ------------------- |
| Fanout   | Broadcast    | Logs globais        |
| Direct   | Exato        | Severidade          |
| Topic    | Padrões      | Módulo + severidade |
| Headers  | Headers AMQP | Filtros complexos   |

***

## ✅ Conclusão

A pasta **`exemplo-headers`** demonstra o uso mais avançado de roteamento oferecido pelo RabbitMQ, permitindo controle refinado sobre o destino das mensagens.

Esse modelo:

*   ✅ É poderoso
*   ✅ É flexível
*   ✅ Resolve cenários complexos
*   ⚠️ É mais verboso que Direct e Topic
