"""
=====================================================
Autor: Saulo Costa
Data de Criação: 01 de maio de 2026

Descrição:
Código desenvolvido para fins educacionais e de aplicação
prática, com foco no aprendizado e na experimentação de
conceitos de mensageria assíncrona utilizando RabbitMQ,
o protocolo AMQP (Advanced Message Queuing Protocol) e
a biblioteca Pika em Python.

Este script atua como um Producer (Sender), publicando
mensagens em uma Exchange do tipo TOPIC.

📌 Observação importante sobre Quorum Queue:
--------------------------------------------
Este Producer é totalmente compatível com filas do tipo
**Quorum Queue**, pois:
- Publica mensagens em uma exchange (desacoplamento)
- Não depende do tipo de fila
- Permite que o Consumer utilize filas quorum,
  garantindo:
    ✅ Alta disponibilidade
    ✅ Replicação entre nós
    ✅ Consistência forte
    ✅ Tolerância a falhas

A definição da Quorum Queue ocorre no lado do Consumer
ou diretamente no broker, através do argumento:
    "x-queue-type": "quorum"

Em uma Topic Exchange:
- As mensagens são roteadas com base em padrões de routing key
- Filas podem ser vinculadas utilizando curingas (* e #)
- Permite roteamento flexível e hierárquico
- Ideal para cenários como logs por componente e severidade
  (ex: api.info, db.error, auth.*)
=====================================================
"""

# Importa a biblioteca pika, utilizada como cliente Python
# para comunicação com o RabbitMQ através do protocolo AMQP.
import pika

# Importa o módulo time para inserir pausas entre os envios,
# facilitando a observação do fluxo de mensagens nos consumers,
# especialmente útil em cenários com filas quorum,
# onde a replicação pode ser observada no broker.
import time


# Define as credenciais explícitas de autenticação
# utilizadas para acessar o RabbitMQ.
#
# O uso de credenciais explícitas é recomendado em
# ambientes distribuídos, frequentemente associados
# a filas quorum e clusters RabbitMQ.
credentials = pika.PlainCredentials("guest", "guest")


# Estabelece uma conexão com o servidor RabbitMQ.
#
# BlockingConnection:
# - Mantém a conexão ativa durante a execução do script
# - Opera de forma síncrona (bloqueante)
#
# Em ambientes com Quorum Queues, o broker pode
# redirecionar automaticamente conexões para líderes
# da fila, mantendo transparência para o Producer.
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="localhost",
        credentials=credentials
    )
)


# Cria um canal de comunicação dentro da conexão.
#
# Conceitos importantes:
# - A conexão representa o vínculo físico com o broker
# - Os canais são leves e reutilizáveis
# - A lógica de quorum ocorre no nível da fila,
#   não impactando o uso do canal pelo Producer
channel = connection.channel()


# Declara a exchange chamada "topic_logs" do tipo TOPIC.
#
# Exchange TOPIC:
# - Utiliza routing keys hierárquicas
# - Permite uso de curingas (* e #)
# - Desacopla Producer de filas
#
# Esse desacoplamento é essencial em arquiteturas
# modernas com Quorum Queues, pois permite:
# ✅ Substituição de filas
# ✅ Escalabilidade
# ✅ Alta disponibilidade
channel.exchange_declare(
    exchange="topic_logs",
    exchange_type="topic"
)


# Lista de mensagens que serão publicadas na exchange.
# Cada item representa o corpo (body) da mensagem AMQP.
#
# Em filas quorum, essas mensagens serão replicadas
# entre múltiplos nós do cluster RabbitMQ.
messages = [
    "A",
    "B",
    "A",
    "A",
    "B"
]


# Lista de severidades que farão parte das routing keys.
#
# A severidade facilita o particionamento lógico
# das mensagens, algo muito comum em sistemas
# críticos que utilizam Quorum Queues.
severities = [
    "info",
    "error",
    "warning",
    "error",
    "info"
]


# Lista de componentes da aplicação.
#
# A combinação componente.severidade gera routing keys
# hierárquicas ideais para Topic Exchanges e
# arquiteturas resilientes baseadas em quorum.
components = [
    "A",
    "B",
    "A",
    "A",
    "B"
]


# Percorre a lista de mensagens e as publica no RabbitMQ.
for i in range(0, 5):

    # Monta a routing key combinando o componente
    # e a severidade da mensagem.
    #
    # Essa chave será utilizada pelo RabbitMQ para
    # decidir quais filas receberão a mensagem,
    # inclusive filas do tipo quorum.
    routing_key = components[i] + "." + severities[i]

    # Publica a mensagem na exchange "topic_logs".
    #
    # O Producer não precisa conhecer:
    # - O tipo da fila (classic ou quorum)
    # - O nó líder da fila
    # - A estratégia de replicação
    #
    # Tudo isso é tratado internamente pelo RabbitMQ
    # em filas quorum.
    channel.basic_publish(
        exchange="topic_logs",
        routing_key=routing_key,
        body=messages[i]
    )

    # Exibe confirmação do envio no console.
    print(f" [x] Enviado:'{routing_key}' - {messages[i]}")

    # Pausa entre envios para facilitar:
    # - Debug
    # - Observação do comportamento do cluster
    time.sleep(1)


# Indica que todas as mensagens foram publicadas.
print("Todas as mensagens foram publicadas com sucesso!")


# Encerra explicitamente a conexão com o RabbitMQ.
#
# Boa prática especialmente importante em
# ambientes distribuídos e com quorum,
# evitando conexões órfãs.
connection.close()
