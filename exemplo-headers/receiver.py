"""
=====================================================================================================
Autor: Saulo Costa

Descrição:
Código educacional e experimental desenvolvido para demonstrar
o consumo de mensagens utilizando RabbitMQ, o protocolo AMQP
 Exchange do tipo HEADERS(Advanced Message Queuing Protocol) e a biblioteca Pika em Python.
- Cria uma fila temporária e exclusiva
- Associa a fila à exchange utilizando cabeçalhos (headers)
- Permanece em estado de escuta, consumindo mensagens
  conforme os critérios definidos nos headers

Em uma Headers Exchange:
- O roteamento NÃO usa routing keys
- As mensagens são roteadas com base em valores de headers
- Permite filtragem avançada por múltiplos atributos
  (ex: componente, severidade, ambiente, etc.)
=====================================================================================================
"""

# Importa a biblioteca pika, utilizada como cliente Python
# para comunicação com o RabbitMQ através do protocolo AMQP.
import pika
import sys


# ----------------------------------------------------------------------------------
# Função callback responsável por processar as mensagens recebidas da fila
# ----------------------------------------------------------------------------------
# Essa função é chamada automaticamente pelo RabbitMQ sempre
# que uma nova mensagem é entregue ao consumer.
def callback(ch, method, properties, body):
    # Exibe os headers da mensagem (utilizados no roteamento)
    # e o corpo da mensagem recebida
    print(" [x] Headers:", properties.headers, "| Mensagem:", body)


# ----------------------------------------------------------------------------------
# Define explicitamente as credenciais de autenticação
# ----------------------------------------------------------------------------------
# - "admin": usuário configurado no broker RabbitMQ
# - "admin": senha associada a esse usuário
#
# O uso de credenciais explícitas evita limitações do
# usuário padrão "guest".
credentials = pika.PlainCredentials("admin", "admin")


# ----------------------------------------------------------------------------------
# Estabelece a conexão com o servidor RabbitMQ
# ----------------------------------------------------------------------------------
# BlockingConnection:
# - Mantém a conexão ativa enquanto o script estiver em execução
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


# ----------------------------------------------------------------------------------
# Cria um canal de comunicação dentro da conexão
# ----------------------------------------------------------------------------------
# Conceitos importantes:
# - A conexão é um recurso pesado e deve ser reutilizada
# - Os canais são leves e utilizados para operações AMQP
#   como declarar exchanges, filas e consumir mensagens
channel = connection.channel()


# ----------------------------------------------------------------------------------
# Declara a exchange "headers_logs" do tipo HEADERS
# ----------------------------------------------------------------------------------
# Exchange HEADERS:
# - Não utiliza routing keys
# - O roteamento é feito com base em pares chave/valor (headers)
# - Ideal para cenários que exigem múltiplos critérios de filtragem
channel.exchange_declare(
    exchange="headers_logs",
    exchange_type="headers"
)


# ----------------------------------------------------------------------------------
# Cria uma fila temporária e exclusiva
# ----------------------------------------------------------------------------------
# Parâmetros:
# - queue="": permite que o RabbitMQ gere um nome automaticamente
# - exclusive=True:
#   → a fila pertence apenas a esta conexão
#   → será removida automaticamente quando a conexão for encerrada
result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue


# ----------------------------------------------------------------------------------
# Obtém os valores de headers informados via linha de comando
# ----------------------------------------------------------------------------------
# Exemplo de execução:
# python receiver.py API error
bindings = sys.argv[1:]

# Caso os parâmetros não sejam informados corretamente,
# o script exibe instruções de uso e encerra a execução.
if len(bindings) < 2:
    sys.stderr.write(
        "Usage: %s <component> <severity>\n" % sys.argv[0]
    )
    sys.exit(1)


# ----------------------------------------------------------------------------------
# Define os headers usados no bind da fila
# ----------------------------------------------------------------------------------
# Esses valores precisam coincidir com os headers
# enviados pelo Producer para que a mensagem seja entregue
headers = {
    "components": sys.argv[1],
    "severities": sys.argv[2],
    "x-match": "any"  # "any": a mensagem é roteada se qualquer header coincidir
}


# ----------------------------------------------------------------------------------
# Associa (bind) a fila à exchange utilizando headers
# ----------------------------------------------------------------------------------
# Parâmetros importantes:
# - exchange: nome da exchange HEADERS
# - queue: fila que receberá as mensagens
# - routing_key: ignorada em exchanges HEADERS
# - arguments=headers: critérios usados no roteamento
channel.queue_bind(
    exchange='headers_logs',
    queue=queue_name,
    routing_key="",
    arguments=headers
)


# Indica que o consumer está ativo e aguardando mensagens
print(
    f" [*] Waiting for logs with headers {headers}. "
    "To exit press CTRL+C"
)


# ----------------------------------------------------------------------------------
# Configura o consumo da fila
# ----------------------------------------------------------------------------------
# auto_ack=True:
# - A mensagem é confirmada automaticamente
# - Simplifica o fluxo
# - Menos segura para cenários críticos
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=True
)


# ----------------------------------------------------------------------------------
# Inicia o loop de consumo contínuo
# ----------------------------------------------------------------------------------
# O script permanecerá em execução até ser interrompido manualmente
# (CTRL+C)
channel.start_consuming()
