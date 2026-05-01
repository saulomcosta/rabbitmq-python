"""
=====================================================
Autor: Saulo Costa

Descrição:
Código educacional e experimental desenvolvido com o
objetivo de demonstrar o consumo de mensagens utilizando
RabbitMQ, o protocolo AMQP (Advanced Message Queuing
Protocol) e a biblioteca Pika em Python.

Este script atua como um Consumer (Receiver) e:
- Conecta-se a um broker RabbitMQ local
- Autentica-se com usuário e senha explícitos
- Declara uma Exchange do tipo DIRECT
- Cria uma fila temporária e exclusiva
- Associa a fila a routing keys específicas (severidades)
- Permanece em estado de escuta, consumindo mensagens
  conforme os critérios de roteamento definidos
=====================================================
"""

# Importa a biblioteca pika, cliente amplamente utilizado
# em Python para comunicação com o RabbitMQ via protocolo AMQP.
import pika
import sys


# Função callback responsável por processar as mensagens
# recebidas da fila.
#
# Essa função é chamada automaticamente sempre que
# uma nova mensagem é entregue ao consumer.
def callback(ch, method, properties, body):
    # Exibe a routing key (severidade) e o corpo da mensagem
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
# - Os canais são leves e utilizados para publicar
#   e consumir mensagens
channel = connection.channel()


# Declara a exchange "direct_logs" do tipo DIRECT.
#
# Exchange DIRECT:
# - Utiliza routing keys para rotear mensagens
# - Apenas filas associadas à mesma routing key
#   receberão a mensagem
# - Ideal para cenários como logs por severidade
channel.exchange_declare(
    exchange="direct_logs",
    exchange_type="direct"
)


# Cria uma fila temporária e exclusiva.
#
# Parâmetros:
# - queue="": permite que o RabbitMQ gere um nome automático
# - exclusive=True:
#   → a fila pertence apenas a esta conexão
#   → será removida automaticamente quando a conexão fechar
result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue


# Obtém as severidades informadas via linha de comando.
#
# Exemplo de execução:
# python receiver.py info warning error
severities = sys.argv[1:]

# Caso nenhuma severidade seja informada, o script
# exibe instruções de uso e encerra a execução.
if not severities:
    sys.stderr.write(
        "Usage: %s [info] [warning] [error]" % sys.argv[0]
    )
    sys.exit(1)


# Realiza o bind da fila com a exchange utilizando
# cada severidade como routing key.
#
# Dessa forma, a fila receberá apenas mensagens
# cuja routing key corresponda às severidades desejadas.
for severity in severities:
    channel.queue_bind(
        exchange='direct_logs',
        queue=queue_name,
        routing_key=severity
    )


# Indica que o consumer está ativo e aguardando mensagens.
print(' [*] Waiting for logs. To exit press CTRL+C')


# Configura o consumo da fila.
#
# Parâmetros:
# - queue=queue_name: fila que será consumida
# - on_message_callback=callback: função de processamento
# - auto_ack=True:
#   → a confirmação (ack) é automática
#   → simplifica o fluxo, porém menos segura em cenários críticos
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=True
)


# Inicia o loop de consumo contínuo.
# O script permanecerá em execução até interrupção manual.
channel.start_consuming()
