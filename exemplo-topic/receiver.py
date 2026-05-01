"""
=====================================================================================================
objetivo de demonstrar o consumo de mensagens utilizando
RabbitMQ, o protocolo AMQP (Advanced Message Queuing
Protocol) e a biblioteca Pika em Python.

Este script atua como um Consumer (Receiver) e:
- Conecta-se a um broker RabbitMQ local
- Autentica-se com usuário e senha explícitos
- Declara uma Exchange do tipo TOPIC
- Cria uma fila temporária e exclusiva
- Associa a fila a padrões de routing keys
- Permanece em estado de escuta, consumindo mensagens
  conforme os critérios de roteamento definidos

Em uma Topic Exchange:
- As mensagens são roteadas por padrões hierárquicos
- É possível utilizar curingas (* e #)
- Permite consumo flexível, como logs por módulo
  e severidade (ex: api.info, db.error, auth.*)
=====================================================
"""

# Importa a biblioteca pika, utilizada como cliente Python
# para comunicação com o RabbitMQ através do protocolo AMQP.
import pika
import sys


# Função callback responsável por processar as mensagens
# recebidas da fila.
#
# Essa função é chamada automaticamente sempre que
# uma nova mensagem é entregue ao consumer.
def callback(ch, method, properties, body):
    # Exibe a routing key utilizada no roteamento
    # e o corpo da mensagem recebida
    print(" [x] %r:%r" % (method.routing_key, body))


# Define explicitamente as credenciais de autenticação
# utilizadas para acessar o RabbitMQ.
#
# - "admin": usuário configurado no broker
# - "admin": senha associada ao usuário
#
# O uso de credenciais explícitas evita limitações do
# usuário padrão "guest".
credentials = pika.PlainCredentials("admin", "admin")


# Estabelece uma conexão com o servidor RabbitMQ.
#
# BlockingConnection:
# - Mantém a conexão ativa enquanto o script estiver rodando
# - Opera de forma síncrona (bloqueante)
#
# ConnectionParameters define:
# - host="localhost": broker RabbitMQ executando localmente
# - credentials=credentials: credenciais de autenticação
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="localhost",
        credentials=credentials
    )
)


# Cria um canal de comunicação dentro da conexão.
#
# Conceitos importantes:
# - A conexão é um recurso pesado
# - Os canais são leves e utilizados para operações AMQP,
#   como declarar exchanges, filas e consumir mensagens
channel = connection.channel()


# Declara a exchange "topic_logs" do tipo TOPIC.
#
# Exchange TOPIC:
# - Utiliza routing keys hierárquicas (ex: api.info)
# - Permite uso de curingas (* e #) nos bindings
# - Possibilita roteamento flexível baseado em padrões
channel.exchange_declare(
    exchange="topic_logs",
    exchange_type="topic"
)


# Cria uma fila temporária e exclusiva.
#
# Parâmetros:
# - queue="": permite que o RabbitMQ gere um nome automaticamente
# - exclusive=True:
#   → a fila pertence apenas a esta conexão
#   → será removida automaticamente quando a conexão for encerrada
result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue


# Obtém os padrões de binding informados via linha de comando.
#
# Exemplo de execução:
# python receiver.py "API.*" "*.error" "#"
bindings = sys.argv[1:]

# Caso nenhum padrão de binding seja informado,
# o script exibe instruções de uso e encerra a execução.
if not bindings:
    sys.stderr.write(
        "Usage: %s [binding_key] [binding_key] ..." % sys.argv[0]
    )
    sys.exit(1)


# Realiza o bind da fila com a exchange utilizando
# cada padrão de routing key informado.
#
# Dessa forma, a fila receberá apenas mensagens
# cujas routing keys correspondam aos padrões definidos.
for binding in bindings:
    channel.queue_bind(
        exchange='topic_logs',
        queue=queue_name,
        routing_key=binding
    )


# Indica que o consumer está ativo e aguardando mensagens.
print(' [*] Waiting for logs. To exit press CTRL+C')


# Configura o consumo da fila.
#
# Parâmetros:
# - queue=queue_name: fila que será consumida
# - on_message_callback=callback: função que processa as mensagens
# - auto_ack=True:
#   → a confirmação (ack) é automática
#   → simplifica o fluxo, porém menos segura em cenários críticos
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=True
)


# Inicia o loop de consumo contínuo.
# O script permanecerá em execução até ser interrompido manualmente.
channel.start_consuming()
