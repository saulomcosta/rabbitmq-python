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
# facilitando a observação do fluxo de mensagens nos consumers.
import time


# Define as credenciais explícitas de autenticação
# utilizadas para acessar o RabbitMQ.
#
# - "admin": usuário configurado no broker
# - "admin": senha associada ao usuário
#
# Essa prática evita restrições impostas ao usuário
# padrão "guest" em versões modernas do RabbitMQ.
credentials = pika.PlainCredentials("guest", "guest")


# Estabelece uma conexão com o servidor RabbitMQ.
#
# BlockingConnection:
# - Mantém a conexão ativa durante a execução do script
# - Opera de forma síncrona (bloqueante)
#
# ConnectionParameters define:
# - host="localhost": RabbitMQ executando localmente
# - credentials=credentials: autenticação utilizada
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
# - Os canais são leves e usados para publicar
#   e consumir mensagens
channel = connection.channel()


# Declara a exchange chamada "topic_logs" do tipo TOPIC.
#
# Exchange TOPIC:
# - Utiliza routing keys hierárquicas
# - Permite uso de curingas (* e #) no binding
# - Possibilita roteamento flexível baseado em padrões
channel.exchange_declare(
    exchange="topic_logs",
    exchange_type="topic"
)


# Lista de mensagens que serão publicadas na exchange.
# Cada item representa o corpo (body) da mensagem AMQP.
messages = [
    "A",
    "B",
    "A",
    "A",
    "B"
]


# Lista de severidades que farão parte das routing keys.
#
# A severidade representa o nível ou tipo do log,
# permitindo que os consumers filtrem mensagens específicas.
severities = [
    "info",
    "error",
    "warning",
    "error",
    "info"
]


# Lista de componentes da aplicação.
#
# Em uma Topic Exchange, a combinação de componentes
# e severidades permite criar routing keys expressivas,
# como: A.info, B.error, etc.
components = ["A"      ,
              "B"      ,
              "A"      ,
              "A"      ,
              "B"        ]


# Percorre a lista de mensagens e as publica no RabbitMQ.
for i in range(0, 5):

    # Monta a routing key combinando o componente
    # e a severidade da mensagem.
    #
    # Essa chave será utilizada pelo RabbitMQ para
    # decidir quais filas receberão a mensagem,
    # conforme os bindings configurados.
    routing_key = components[i] + "." + severities[i]

    # Publica a mensagem na exchange "topic_logs".
    #
    # Parâmetros:
    # - exchange="topic_logs": exchange do tipo TOPIC
    # - routing_key=routing_key: chave usada no roteamento
    # - body=messages[i]: conteúdo da mensagem
    #
    # Apenas consumers com bindings compatíveis
    # com esse padrão de routing key receberão a mensagem.
    channel.basic_publish(
        exchange="topic_logs",
        routing_key=routing_key,
        body=messages[i]
    )

    # Exibe confirmação do envio no console.
    print(f" [x] Enviado:'{routing_key}' - {messages[i]}")

    # Pausa de 1 segundo entre os envios,
    # facilitando a visualização do fluxo.
    time.sleep(1)


# Indica que todas as mensagens foram publicadas.
print("Todas as mensagens foram publicadas com sucesso!")


# Encerra explicitamente a conexão com o RabbitMQ.
# Boa prática para liberação de recursos de rede e memória.
connection.close()
