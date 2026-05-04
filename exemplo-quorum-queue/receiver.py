"""
=====================================================
Autor: Saulo Costa

Descrição:
Script educacional para demonstrar o consumo de mensagens
utilizando RabbitMQ, o protocolo AMQP (Advanced Message
Queuing Protocol) e a biblioteca Pika em Python.

Este script atua como um Consumer (Receiver) e foi
estruturado para trabalhar com **Quorum Queues**,
um tipo de fila voltado para alta disponibilidade
e consistência forte em clusters RabbitMQ.

O Consumer:
- Conecta-se a um broker RabbitMQ local
- Autentica-se com credenciais explícitas
- Declara uma Exchange do tipo TOPIC
- Declara uma **fila do tipo Quorum**
- Associa a fila a padrões de routing keys via CLI
- Consome mensagens de forma controlada (ACK/NACK)
- Rejeita mensagens, permitindo reentrega limitada
- Encaminha mensagens excedentes para uma DLX/DLQ

Conceitos demonstrados:
- Topic Exchange
- Routing Keys hierárquicas
- Curingas (* e #)
- Quorum Queue
- Leader / Followers (conceito)
- Delivery Limit
- Dead Letter Exchange (DLX)
- Dead Letter Queue (DLQ)
- Fluxo de rejeição com basic_nack
=====================================================
"""

# Importa a biblioteca pika, utilizada como cliente Python
# para comunicação com o RabbitMQ via protocolo AMQP.
import pika
import sys


# Callback responsável por processar mensagens recebidas
# a partir de uma fila do tipo Quorum.
#
# Em Quorum Queues:
# - A mensagem é entregue pelo nó líder da fila
# - A confirmação (ack/nack) também é tratada pelo líder
def callback(ch, method, properties, body):
    # Exibe a routing key utilizada no roteamento
    # e o corpo da mensagem recebida
    print(" [x] %r:%r" % (method.routing_key, body))

    # Rejeita explicitamente a mensagem consumida.
    #
    # requeue=True:
    # - A mensagem retorna para a Quorum Queue
    # - O contador interno de entregas é incrementado
    # - O RabbitMQ controla esse número via x-delivery-limit
    #
    # Quando o limite é atingido, a mensagem é
    # automaticamente encaminhada para a DLX.
    channel.basic_nack(
        delivery_tag=method.delivery_tag,
        requeue=True
    )


# Credenciais explícitas de autenticação.
#
# Em ambientes com Quorum Queues, geralmente
# existe um cluster RabbitMQ, tornando o uso
# de credenciais explícitas uma boa prática.
credentials = pika.PlainCredentials("guest", "guest")


# Estabelece uma conexão com o RabbitMQ.
#
# BlockingConnection:
# - Mantém a conexão ativa
# - Opera de forma síncrona
#
# Em Quorum Queues, o broker pode redirecionar
# automaticamente a comunicação para o nó líder
# da fila, sem impacto para o cliente.
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="localhost",
        credentials=credentials
    )
)


# Cria um canal de comunicação AMQP.
#
# Observações:
# - A conexão é um recurso pesado
# - Os canais são leves
# - Toda interação com filas quorum ocorre via canal
channel = connection.channel()


# Declara a Dead Letter Exchange (DLX).
#
# A DLX recebe mensagens que:
# - Excederam o delivery-limit
# - Foram rejeitadas sem requeue
# - Expiraram por TTL (se configurado)
channel.exchange_declare(
    exchange="dlx_logs",
    exchange_type="topic"
)


# Declara a Dead Letter Queue (DLQ).
#
# Esta fila pode ser classic ou quorum,
# dependendo do cenário desejado.
result = channel.queue_declare(
    queue="dlq_logs",
    durable=True
)


# Realiza o bind da DLQ com a DLX.
#
# O curinga "#" garante que todas
# as mensagens direcionadas à DLX
# sejam armazenadas nesta fila.
channel.queue_bind(
    exchange="dlx_logs",
    queue="dlq_logs",
    routing_key="#"
)


# Declara a exchange principal do tipo TOPIC.
#
# Essa exchange desacopla producers de consumers,
# o que é fundamental em arquiteturas baseadas
# em Quorum Queues.
channel.exchange_declare(
    exchange="topic_logs",
    exchange_type="topic"
)


# Declara explicitamente uma **Quorum Queue**.
#
# Características importantes:
# - durable=True → a fila sobrevive a reinicializações
# - x-queue-type=quorum → define a fila como quorum
# - Mensagens são replicadas entre nós do cluster
# - Um nó líder coordena as entregas
# - Consistência forte baseada em Raft
#
# x-delivery-limit:
# - Define quantas tentativas de entrega uma mensagem pode ter
# - Após exceder o limite, a mensagem é encaminhada para a DLX
result = channel.queue_declare(
    queue="teste-quorum",
    durable=True,
    arguments={
        "x-queue-type": "quorum",
        "x-dead-letter-exchange": "dlx_logs",
        "x-dead-letter-routing-key": "NEW_Key",
        "x-delivery-limit": 5
    }
)

queue_name = result.method.queue


# Obtém os padrões de binding via linha de comando.
#
# Exemplo:
# python consumer_topic.py "A.*" "*.error"
bindings = sys.argv[1:]


# Caso nenhum binding seja informado,
# o script encerra sua execução.
if not bindings:
    sys.stderr.write(
        "Usage: %s [binding_key] [binding_key] ..." % sys.argv[0]
    )
    sys.exit(1)


# Realiza o bind da Quorum Queue com a Topic Exchange.
#
# Apenas mensagens cujas routing keys coincidirem
# com os padrões informados serão entregues.
for binding in bindings:
    channel.queue_bind(
        exchange="topic_logs",
        queue=queue_name,
        routing_key=binding
    )


# Indica que o Consumer está ativo
print(" [*] Waiting for logs. To exit press CTRL+C")


# Configura o consumo da Quorum Queue.
#
# auto_ack=False:
# - Exige ack/nack explícito
# - Essencial em filas quorum para
#   controle preciso de falhas
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=False
)


# Inicia o loop de consumo contínuo.
#
# O RabbitMQ controla:
# - Redelivery
# - Delivery limit
# - Encaminhamento para DLQ
channel.start_consuming()
