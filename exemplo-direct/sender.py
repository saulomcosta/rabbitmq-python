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
mensagens em uma Exchange do tipo DIRECT.

Em uma Direct Exchange:
- As mensagens são roteadas com base na routing_key
- Somente filas vinculadas com a mesma binding key
  receberão a mensagem
- Ideal para cenários de roteamento seletivo, como
  logs por severidade (info, warning, error, etc.)
=====================================================
"""

# Importa a biblioteca pika, utilizada como cliente Python
# para comunicação com o RabbitMQ através do protocolo AMQP.
import pika

# Importa o módulo time para inserir pausas entre os envios,
# facilitando a observação do fluxo de mensagens nos Receivers.
import time


# Define as credenciais explícitas de autenticação
# utilizadas para acessar o RabbitMQ.
#
# - "admin": usuário configurado no broker
# - "admin": senha associada ao usuário
#
# Essa prática evita restrições impostas ao usuário
# padrão "guest" em brokers RabbitMQ mais recentes.
credentials = pika.PlainCredentials("admin", "admin")


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
# - Os canais são leves e devem ser usados para publicar
#   e consumir mensagens
channel = connection.channel()


# Declara uma exchange chamada "direct_logs" do tipo DIRECT.
#
# Exchange DIRECT:
# - Utiliza routing keys para roteamento
# - Apenas filas com binding keys iguais à routing_key
#   da mensagem receberão o conteúdo
# - Muito utilizada para logs, eventos categorizados
#   ou filas específicas por tipo de mensagem
channel.exchange_declare(
    exchange="direct_logs",
    exchange_type="direct"
)


# Lista de mensagens que serão publicadas na exchange.
# Cada item representa o corpo da mensagem AMQP.
messages = [
    "Primeira log exchange 1",
    "Segunda log exchange 2",
    "Terceira log exchange 3",
    "Quarta log exchange 4",
    "Quinta log exchange 5"
]


# Lista de severidades utilizadas como routing keys.
#
# Essas chaves determinam para quais filas as mensagens
# serão entregues, de acordo com o binding configurado
# no Receiver.
severities = [
    "info",
    "warning",
    "error",
    "critical",
    "debug"
]


# Percorre a lista de mensagens e as publica no RabbitMQ.
for i in range(len(messages)):

    # Publica a mensagem na exchange "direct_logs".
    #
    # Parâmetros:
    # - exchange="direct_logs": exchange do tipo DIRECT
    # - routing_key=severities[i]: chave usada para roteamento
    # - body=messages[i]: conteúdo da mensagem
    #
    # Apenas Receivers vinculados com a mesma binding key
    # receberão essa mensagem.
    channel.basic_publish(
        exchange="direct_logs",
        routing_key=severities[i],
        body=messages[i]
    )

    # Exibe confirmação do envio no console.
    print(f" [x] Enviado: '{messages[i]}' | severity='{severities[i]}'")

    # Pausa de 1 segundo entre os envios,
    # facilitando a visualização do fluxo.
    time.sleep(1)


# Indica que todas as mensagens foram enviadas.
print("Todas as mensagens foram publicadas com sucesso!")


# Encerra explicitamente a conexão com o RabbitMQ.
# Boa prática para liberação de recursos de rede e memória.
connection.close()
