# 📂 Pasta `exemplo-direct`

## 📌 Visão Geral

A pasta **`exemplo-direct`** contém exemplos educacionais e práticos que demonstram o uso de **Direct Exchange** no RabbitMQ, utilizando o **protocolo AMQP** e a biblioteca **Pika em Python**.

O objetivo principal é ilustrar:

*   Como funciona o **roteamento seletivo de mensagens**
*   O papel da **routing key** em uma Direct Exchange
*   A separação clara entre **Producer (Sender)** e **Consumer (Receiver)**
*   Como diferentes severidades podem ser usadas para controlar o fluxo das mensagens

Esse padrão é muito comum em cenários como **logs por severidade**, **eventos categorizados** e **processamento específico de mensagens**.

***

## 🧱 Estrutura dos Arquivos

    exemplo-direct/
    ├── producer_direct.py
    ├── consumer_direct.py
    └── doc/README.md

***

## 📜 Descrição dos Arquivos

### 🔹 `producer_direct.py`

### O que é

Script responsável por **produzir (enviar)** mensagens para o RabbitMQ utilizando uma **Direct Exchange**.

### O que ele faz

*   Conecta-se a um broker RabbitMQ local
*   Autentica-se com credenciais explícitas (`admin/admin`)
*   Declara a exchange `direct_logs` do tipo **DIRECT**
*   Publica mensagens com diferentes **routing keys** (severidades)
*   Envia mensagens de forma sequencial, com pausa entre os envios

### Conceitos demonstrados

*   Producer RabbitMQ
*   Declaração de `exchange_type="direct"`
*   Uso de `routing_key` para roteamento
*   Envio seletivo de mensagens

### Exemplo de routing keys usadas

```text
info
warning
error
critical
debug
```

Cada mensagem enviada pelo Producer carrega uma **routing key específica**, que será usada pelo RabbitMQ para decidir **quais filas receberão a mensagem**.

***

### 🔹 `consumer_direct.py`

### O que é

Script responsável por **consumir (receber)** mensagens publicadas na Direct Exchange, filtrando-as de acordo com a routing key.

### O que ele faz

*   Conecta-se ao RabbitMQ local
*   Autentica-se com usuário e senha explícitos
*   Declara a mesma exchange `direct_logs`
*   Cria uma **fila temporária e exclusiva**
*   Faz o **bind da fila** com uma ou mais severidades
*   Permanece em escuta contínua aguardando mensagens

### Conceitos demonstrados

*   Consumer RabbitMQ
*   Bind seletivo com routing keys
*   Fila exclusiva (`exclusive=True`)
*   Consumo de mensagens de acordo com severidade

### Uso de argumentos na execução

O Consumer recebe as severidades pela linha de comando:

```bash
python consumer_direct.py info warning error
```

Nesse exemplo, o Consumer **só receberá mensagens** cuja routing key seja:

*   `info`
*   `warning`
*   `error`

Mensagens com outras severidades (**debug**, **critical**) **não serão entregues a essa fila**.

***

## 🔄 Fluxo de Funcionamento (Direct Exchange)

1.  O **Producer** envia mensagens para a exchange `direct_logs`
2.  Cada mensagem contém uma **routing key** (ex: `info`)
3.  O **RabbitMQ** compara a routing key da mensagem com os **bindings das filas**
4.  Apenas filas que possuam **binding keys exatamente iguais** recebem a mensagem
5.  O **Consumer** processa apenas as mensagens compatíveis

📌 **Importante:**
Em uma Direct Exchange, o roteamento é **exato** — não há curingas.

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

#### 1️⃣ Inicie o Consumer

Em um terminal, execute informando as severidades desejadas:

```bash
python consumer_direct.py info error
```

O Consumer ficará aguardando mensagens com essas severidades.

***

#### 2️⃣ Execute o Producer

Em outro terminal:

```bash
python producer_direct.py
```

O Producer enviará mensagens com várias severidades.

***

### ✅ Resultado esperado

*   O Consumer **receberá apenas as mensagens** compatíveis com as severidades informadas
*   Mensagens com routing keys diferentes **não aparecerão**

***

## 📊 Quando Usar Direct Exchange

A **Direct Exchange** é indicada quando:

*   Você precisa de **roteamento preciso**
*   Cada mensagem deve ir para **filas específicas**
*   O critério de roteamento é **bem definido**
    (ex: nível de log, tipo de evento, categoria)

### Exemplos de uso real

*   Logs por severidade
*   Processamento por tipo de evento
*   Sistemas de alerta
*   Mensagens direcionadas a serviços específicos

***

## ✅ Conclusão

A pasta **`exemplo-direct`** demonstra claramente como o RabbitMQ permite **controle total do destino das mensagens** utilizando Direct Exchange.

Esse modelo:

*   ✅ É simples
*   ✅ É eficiente
*   ✅ Facilita a escalabilidade
*   ✅ É amplamente utilizado em sistemas distribuídos

