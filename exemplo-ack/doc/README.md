# 📂 Pasta `exemplo-ack`

## 📌 Visão Geral

A pasta **`exemplo-ack`** contém exemplos práticos e educacionais sobre **mensageria assíncrona com RabbitMQ**, utilizando o **protocolo AMQP** e a biblioteca **Pika em Python**, com foco principal no conceito de **ACK (Acknowledgement)**.

O objetivo é demonstrar:

*   Como funciona o envio e consumo de mensagens
*   A diferença prática entre **ACK automático (`auto_ack=True`)** e **ACK manual (`auto_ack=False`)**
*   Como o RabbitMQ garante (ou não) a confiabilidade no processamento das mensagens

Esses exemplos são ideais para **estudos**, **testes** e como **base para projetos reais**.

***

## 🧱 Estrutura dos Arquivos

    exemplo-ack/
    ├── producer.py
    ├── consumer_ack_false.py
    ├── consumer_ack_true.py
    └── doc/README.md

***

## 📜 Descrição de Cada Arquivo

### 🔹 `producer.py`

**O que é:**
Script responsável por **produzir (enviar)** mensagens para o RabbitMQ.

**O que ele faz:**

*   Conecta-se ao RabbitMQ local
*   Declara a fila `hello`
*   Envia uma sequência de mensagens (com intervalo de 1 segundo)
*   Usa a **exchange padrão (`""`)**, roteando diretamente para a fila

**Conceitos demonstrados:**

*   Producer básico
*   Uso de `basic_publish`
*   Envio sequencial de mensagens
*   Funcionamento do *default exchange*

✅ **Esse arquivo é comum a ambos os exemplos de ACK**.

***

### 🔹 `consumer_ack_true.py` (ACK Automático)

**O que é:**
Consumer configurado com **ACK automático**.

**Configuração-chave:**

```python
channel.basic_consume(
    queue="hello",
    on_message_callback=callback,
    auto_ack=True
)
```

**O que acontece nesse modo:**

*   O RabbitMQ considera a mensagem **processada assim que é entregue**
*   Não há confirmação explícita por parte do consumidor
*   Se o consumer falhar durante o processamento:
    *   ❌ A mensagem **é perdida**
    *   ❌ O RabbitMQ NÃO reenvia a mensagem

**Quando usar:**

*   Logs simples
*   Eventos não críticos
*   Cenários onde perda de mensagens é aceitável

✅ **Mais simples**
⚠️ **Menos confiável**

***

### 🔹 `consumer_ack_false.py` (ACK Manual)

**O que é:**
Consumer configurado com **ACK manual**, garantindo confiabilidade.

**Configuração-chave:**

```python
channel.basic_consume(
    queue="hello",
    on_message_callback=callback,
    auto_ack=False
)
```

Dentro do `callback`, o ACK é enviado manualmente:

```python
ch.basic_ack(delivery_tag=method.delivery_tag)
```

**O que acontece nesse modo:**

*   A mensagem só é removida da fila **após confirmação explícita**
*   Se o consumer falhar antes do ACK:
    *   ✅ A mensagem **retorna para a fila**
    *   ✅ Pode ser reprocessada por outro consumer

**Quando usar:**

*   Processos críticos
*   Pagamentos
*   Integrações importantes
*   Qualquer cenário onde **não pode haver perda de mensagens**

⚠️ **Mais verboso**
✅ **Muito mais seguro**

***

## 🔄 Diferença Prática: `ack=True` vs `ack=False`

| Característica             | auto\_ack=True        | auto\_ack=False    |
| -------------------------- | --------------------- | ------------------ |
| Confirmação automática     | ✅ Sim                 | ❌ Não              |
| Ack manual necessário      | ❌ Não                 | ✅ Sim              |
| Risco de perda de mensagem | ⚠️ Alto               | ✅ Baixo            |
| Reentrega em caso de falha | ❌ Não                 | ✅ Sim              |
| Complexidade               | 🟢 Baixa              | 🟡 Média           |
| Uso recomendado            | Logs, eventos simples | Processos críticos |

***

## ▶️ Como Executar os Exemplos

### ✅ Pré-requisitos

*   RabbitMQ em execução
*   Python 3.9+
*   Biblioteca Pika instalada:

```bash
pip install pika
```

*   Usuário configurado no RabbitMQ:
    *   usuário: `admin`
    *   senha: `admin`

***

### ✅ Passo a Passo

#### 1️⃣ Inicie o RabbitMQ

Certifique-se de que o serviço está rodando localmente (`localhost:5672`).

***

#### 2️⃣ Execute o Consumer (escolha um)

ACK automático:

```bash
python receiver.py
```

ACK manual:

```bash
python receiverNoAck.py
```

***

#### 3️⃣ Execute o Producer

Em outro terminal:

```bash
python sender.py
```

***

## 📈 O Que Observar nos Testes

*   No **ACK automático**, ao interromper o consumer durante o processamento:
    *   As mensagens em andamento **são perdidas**

*   No **ACK manual**, ao interromper o consumer:
    *   As mensagens **não confirmadas voltam para a fila**

Esse comportamento pode ser observado claramente no **RabbitMQ Management UI**.

***

## 🎯 Objetivo Educacional

Este exemplo ajuda a entender:

*   Como o RabbitMQ garante confiabilidade
*   Quando usar ACK manual ou automático
*   A importância do ACK em sistemas distribuídos
*   Boas práticas para consumidores críticos

***

## ✅ Conclusão

A pasta **`exemplo-ack`** mostra, de forma prática e clara, que:

> **ACK não é detalhe — é parte fundamental do design de sistemas confiáveis.**

Escolher entre `auto_ack=True` ou `auto_ack=False` depende diretamente do **nível de criticidade do seu sistema**.
