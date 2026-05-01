"""
================================================ Queuing Protocol)=====================================================
e a biblioteca Pika em Python.

Este script atua como um Producer (Sender), publicando
mensagens em uma Exchange do tipo HEADERS.

Em uma Headers Exchange:
- O roteamento NÃO utiliza routing keys
- As mensagens são roteadas com base em pares chave/valor
  definidos nos headers da mensagem
- Permite filtros mais complexos e combinados
  (ex: componente + severidade)
- Ideal para cenários onde múltiplos atributos
  determinam o destino da mensagem
=====================================================
"""

# Importa o módulo time para inserir pausas entre os envios,
# facilitando a visualização do fluxo de mensagens.
import time

# Importa a biblioteca pika, utilizada como cliente Python
# para comunicação com o RabbitMQ através do protocolo AMQP.
import pika

# Importa sys (não utilizado diretamente neste script,
# mas comum em exemplos para expansão futura).
import sys


# -----------------------------------------------------
# Define as credenciais explícitas de autenticação
# -----------------------------------------------------
# - "admin": usuário configurado no broker RabbitMQ
# - "admin": senha associada a esse usuário
#
# O uso de credenciais explícitas evita limitações
# do usuário padrão "guest".
credentials = pika.PlainCredentials("admin", "admin")


# -----------------------------------------------------
# Estabelece a conexão com o servidor RabbitMQ
# -----------------------------------------------------
# BlockingConnection:
# - Mantém a conexão ativa durante a execução do script
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


# -----------------------------------------------------
# Cria um canal de comunicação dentro da conexão
# -----------------------------------------------------
# Conceitos importantes:
# - A conexão é um recurso pesado
# - Os canais são leves e utilizados para operações AMQP,
#   como declarações e publicação de mensagens
channel = connection.channel()


# -----------------------------------------------------
# Declara a exchange "headers_logs" do tipo HEADERS
# -----------------------------------------------------
# Exchange HEADERS:
# - O roteamento é feito exclusivamente pelos headers
# - routing_key é ignorada nesse tipo de exchange
# - Ideal para cenários com múltiplos critérios de filtragem
channel.exchange_declare(
    exchange="headers_logs",
    exchange_type="headers"
)


# -----------------------------------------------------
# Mensagens que serão publicadas
# -----------------------------------------------------
# Cada item representa o corpo (body) da mensagem AMQP
messages = [
    "Primeiro log",
    "Segundo log",
    "Terceiro log",
    "Quarto log",
    "Quinto log"
]


# -----------------------------------------------------
# Níveis de severidade associados às mensagens
# -----------------------------------------------------
# Esses valores serão enviados como headers, não como
# routing keys.
severities = [
    "info",
    "error",
    "warning",
    "error",
    "info"
]


# -----------------------------------------------------
# Componentes da aplicação associados às mensagens
# -----------------------------------------------------
# Juntamente com a severidade, formam os critérios
# de roteamento da Headers Exchange.
components = [
    "A",
    "B",
    "A",
    "A",
    "B"
]


# -----------------------------------------------------
# Publicação das mensagens no RabbitMQ
# -----------------------------------------------------
# Para cada mensagem:
# - Define-se um conjunto de headers
# - A mensagem é publicada na exchange HEADERS
# - routing_key é deixada vazia (não utilizada)
for i in range(0, 5):

    # Cria as propriedades da mensagem com headers personalizados
    props = pika.BasicProperties(
        headers={
            "components": components[i],
            "severities": severities[i]
        }
    )

    # Publica a mensagem na exchange "headers_logs"
    channel.basic_publish(
        exchange="headers_logs",
        routing_key="",          # Ignorado em exchanges HEADERS
        body=messages[i],
        properties=props
    )

    # Exibe confirmação do envio no console
    print(
        f" [x] Enviado: headers={{components:{components[i]}, "
        f"severities:{severities[i]}}} - {messages[i]}"
    )

    # Pausa de 1 segundo entre os envios
    time.sleep(1)


# -----------------------------------------------------
# Encerra explicitamente a conexão com o RabbitMQ
# -----------------------------------------------------
# Boa prática para liberação de recursos de rede e memória
connection.close()
