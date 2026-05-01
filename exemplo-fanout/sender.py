""" Saulo Costa
Data de Criação: 01 de maio de 2026

Descrição:
Código desenvolvido para fins educacionais e de aplicação
prática, com foco no aprendizado e na experimentação de
conceitos de mensageria assíncrona utilizando RabbitMQ,
o protocolo AMQP e a biblioteca Pika em Python.

Este script atua como um Producer (Sender), publicando
mensagens em uma Exchange do tipo fanout, permitindo
a distribuição das mensagens para múltiplas filas
conectadas, servindo como base para estudos, testes
e evolução de soluções orientadas a mensagens.
=====================================================
"""

# Importa a biblioteca pika, utilizada como cliente Python
# para comunicação com o RabbitMQ através do protocolo AMQP.
import pika

# Importa o módulo time, utilizado para inserir pausas
# entre o envio das mensagens, facilitando a observação
# do fluxo de dados no consumer.
import time


# Define as credenciais explícitas de autenticação
# utilizadas para acessar o RabbitMQ.
#
# - "admin": usuário configurado no broker
# - "admin": senha associada ao usuário
#
# Essa abordagem evita restrições impostas ao usuário
# padrão "guest" nas versões mais recentes do RabbitMQ.
credentials = pika.PlainCredentials("admin", "admin")


# Estabelece uma conexão com o servidor RabbitMQ.
#
# BlockingConnection:
# - Mantém a conexão ativa durante a execução do script
# - Opera de forma síncrona, aguardando respostas do broker
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
# - A conexão é um recurso pesado
# - Os canais são leves e recomendados para operações
#   de envio e recebimento de mensagens
channel = connection.channel()


# Declara uma exchange chamada "logs" do tipo fanout.
#
# Exchange fanout:
# - Ignora routing keys
# - Replica a mensagem para todas as filas associadas
# - Indicada para cenários de broadcast (logs, eventos, alertas)
channel.exchange_declare(
    exchange="logs",
    exchange_type="fanout"
)


# Declara a fila chamada "hello".
#
# Comportamento do RabbitMQ:
# - Se a fila não existir, ela será criada
# - Se já existir, será reutilizada
#
# Observação:
# Para que a fila receba mensagens da exchange fanout,
# é necessário que exista um bind entre a fila e a exchange.
channel.queue_declare(queue="hello")


# Lista de mensagens que serão publicadas na exchange.
# Cada item representa o corpo (body) de uma mensagem AMQP.
message = [
    "Primeira log exchange 1",
    "Segunda log exchange 2",
    "Terceira log exchange 3",
    "Quarta log exchange 4",
    "Quinta log exchange 5"
]


# Percorre a lista de mensagens e as publica no RabbitMQ.
for msg in message:

    # Publica a mensagem na exchange "logs".
    #
    # Parâmetros:
    # - exchange="logs": exchange do tipo fanout
    # - routing_key="": ignorada nesse tipo de exchange
    # - body=msg: conteúdo da mensagem (convertido para bytes)
    channel.basic_publish(
        exchange="logs",
        routing_key="",
        body=msg
    )

    # Exibe no console uma confirmação do envio da mensagem.
    print(f" [x] Enviado: {msg}")

    # Pausa de 1 segundo entre os envios,
    # facilitando a visualização do consumo.
    time.sleep(1)


# Mensagem final indicando que todas as mensagens
# foram publicadas com sucesso.
print("Mensagens enviadas!")


# Encerra explicitamente a conexão com o RabbitMQ.
# Boa prática para liberação de recursos de rede e memória.
connection.close()
