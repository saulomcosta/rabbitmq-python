"""
=====================================================
Autor: Saulo Costa

Descrição:
Script educMQ, o protocolo AMQP (Advanced Message QueuingScript educacional para demonstrar o consumo de mensagens
Protocol) e a biblioteca Pika em Python.

Este script atua como um Consumer (Receiver) e:
- Conecta-se a um broker RabbitMQ local
- Autentica-se com credenciais explícitas
- Declara uma Exchange do tipo TOPIC
- Cria uma fila temporária e exclusiva
- Associa a fila a padrões de routing keys informados via CLI
- Permanece em estado de escuta, consumindo mensagens
- Rejeita mensagens consumidas para envio a uma Dead Letter Exchange

Conceitos demonstrados:
- Topic Exchange
- Routing Keys hierárquicas
- Uso de curingas (* e #)
- Dead Letter Exchange (DLX)
- Dead Letter Queue (DLQ)
- Fluxo de rejeição com basic_nack
=====================================================
"""

# Importa a biblioteca pika, utilizada como cliente Python
# para comunicação com o RabbitMQ através do protocolo AMQP.
import pika
import sys


# Função callback responsável por processar as mensagens
# recebidas a partir da fila associada à exchange.
#
# Esta função é chamada automaticamente pelo Pika sempre que
# uma nova mensagem é entregue ao consumer.
def callback(ch, method, properties, body):
    # Exibe no console a routing key utilizada no roteamento
    # e o corpo da mensagem recebida
    print(" [x] %r:%r" % (method.routing_key, body))

    # Rejeita explicitamente a mensagem consumida.
    # Como requeue=False, a mensagem não retorna à fila original
    # e será encaminhada para a Dead Letter Exchange (se configurada).
    channel.basic_nack(
        delivery_tag=method.delivery_tag,
        requeue=False # Caso True, a mensagem seria reencaminhada para a fila original
    )


# Define explicitamente as credenciais de autenticação
# utilizadas para acessar o RabbitMQ.
#
# O uso de credenciais explícitas evita limitações impostas
# ao usuário padrão "guest" em ambientes não locais.
credentials = pika.PlainCredentials("guest", "guest")


# Estabelece uma conexão com o servidor RabbitMQ.
#
# BlockingConnection:
# - Mantém a conexão ativa enquanto o script estiver em execução
# - Opera de forma síncrona (bloqueante)
#
# ConnectionParameters define:
# - host="localhost": broker RabbitMQ executando localmente
# - credentials=credentials: credenciais utilizadas na autenticação
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="localhost",
        credentials=credentials
    )
)


# Cria um canal de comunicação dentro da conexão.
#
# Observações importantes:
# - A conexão é um recurso pesado
# - Os canais são leves e devem ser reutilizados
# - Todas as operações AMQP ocorrem através do canal
channel = connection.channel()


# Declara a Dead Letter Exchange (DLX), responsável por
# receber mensagens rejeitadas por filas associadas a ela.
channel.exchange_declare(
    exchange="dlx_logs",
    exchange_type="topic"
)

# Declara a Dead Letter Queue (DLQ), que armazenará
# as mensagens redirecionadas pela DLX.
result = channel.queue_declare(
    queue="dlq_logs"
)


# Associa a DLQ à DLX utilizando o curinga "#",
# permitindo receber todas as mensagens rejeitadas.
channel.queue_bind(
    exchange="dlx_logs",
    queue="dlq_logs",
    routing_key="#"
)


# Declara a exchange principal "topic_logs" do tipo TOPIC.
#
# Exchange TOPIC:
# - Roteia mensagens com base em padrões hierárquicos
# - Permite o uso de curingas (* e #)
# - Possibilita filtros flexíveis por tipo de mensagem
channel.exchange_declare(
    exchange="topic_logs",
    exchange_type="topic"
)


# Cria uma fila temporária e exclusiva para este consumer.
#
# Parâmetros:
# - queue="": permite que o RabbitMQ gere um nome automaticamente
# - exclusive=True:
#   → a fila pertence apenas a esta conexão
#   → será removida automaticamente quando a conexão for encerrada
# - arguments:
#   → associa a fila a uma Dead Letter Exchange
result = channel.queue_declare(
    "",
    exclusive=True,
    arguments={
        "x-dead-letter-exchange": "dlx_logs",
        "x-dead-letter-routing-key": "NEW_Key" # Opcional: define uma routing key específica para mensagens rejeitadas
    }
)

queue_name = result.method.queue


# Obtém os padrões de binding informados via linha de comando.
#
# Exemplo de execução:
# python receiver.py "A.*" "*.error" "#"
bindings = sys.argv[1:]


# Caso nenhum padrão seja informado, o script exibe
# instruções básicas de uso e encerra a execução.
if not bindings:
    sys.stderr.write(
        "Usage: %s [binding_key] [binding_key] ..." % sys.argv[0]
    )
    sys.exit(1)


# Associa a fila criada à exchange "topic_logs" utilizando
# cada padrão de routing key informado.
#
# Apenas mensagens cujas routing keys correspondam
# aos padrões configurados serão entregues a esta fila.
for binding in bindings:
    channel.queue_bind(
        exchange="topic_logs",
        queue=queue_name,
        routing_key=binding
    )


# Indica no console que o consumer está ativo
# e aguardando mensagens.
print(" [*] Waiting for logs. To exit press CTRL+C")


# Configura o consumo da fila.
#
# Parâmetros:
# - queue=queue_name: fila consumida
# - on_message_callback=callback: função de processamento
# - auto_ack=False:
#   → exige confirmação manual (ack/nack)
#   → permite controle explícito de falhas
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=False
)


# Inicia o loop de consumo contínuo.
# O script permanecerá em execução até ser interrompido manualmente.
channel.start_consuming()
