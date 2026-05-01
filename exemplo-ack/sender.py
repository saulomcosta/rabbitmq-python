"""
=====================================================
 Autor: Saulo Costa
 Data de Criação: 01 de maio de 2026
 Descrição:
 Criação desenvolvida por Saulo Costa com fins de estudo e aplicação prática, voltada ao aprendizado e experimentação de #  conceitos técnicos, incluindo programação em Python e integração com sistemas de mensageria (RabbitMQ / AMQP). O conteúdo tem caráter educacional e pode servir como base para estudos, testes e evolução de soluções futuras.
=====================================================
"""

# Importa a biblioteca pika, que é o cliente Python para RabbitMQ.
# Ela implementa o protocolo AMQP (Advanced Message Queuing Protocol).
import pika

# Importa a biblioteca time, usada aqui apenas para inserir um atraso
# entre o envio das mensagens, simulando um envio gradual.
import time


# Cria um objeto de credenciais explícitas de autenticação.
# - "admin" é o nome do usuário criado no RabbitMQ
# - "admin" é a senha desse usuário
#
# Isso evita o uso do usuário "guest", que possui várias restrições
# de acesso nas versões mais recentes do RabbitMQ.
credentials = pika.PlainCredentials("admin", "admin")


# Cria uma conexão com o servidor RabbitMQ.
# BlockingConnection significa que o código Python ficará "bloqueado"
# aguardando resposta do RabbitMQ a cada operação.
#
# ConnectionParameters define:
# - host="localhost": RabbitMQ está rodando na mesma máquina
# - credentials=credentials: usa as credenciais definidas acima
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="localhost",
        credentials=credentials
    )
)


# Cria um "channel" (canal) dentro da conexão.
#
# No RabbitMQ:
# - Uma conexão é pesada e cara
# - Um channel é leve
# - Sempre publicamos e consumimos mensagens através de canais
channel = connection.channel()


# Declara uma fila chamada "hello".
#
# Observações importantes:
# - Se a fila já existir, o RabbitMQ NÃO cria outra, apenas reutiliza
# - Se não existir, ela é criada automaticamente
# - Isso torna o código idempotente (seguro para múltiplas execuções)
channel.queue_declare(queue="hello")


# Lista de mensagens que serão enviadas para a fila.
# Cada item da lista representa o corpo (body) de uma mensagem AMQP.
message = [
    "Primeira mensagem",
    "Segunda mensagem",
    "Terceira mensagem",
    "Quarta mensagem",
    "Quinta mensagem"
]


# Loop que percorre cada mensagem da lista
# e a envia para o RabbitMQ.
for msg in message:

    # Envia a mensagem para o broker RabbitMQ.
    #
    # Parâmetros:
    # - exchange="": exchange padrão (default exchange)
    #   → nesse caso, o routing_key deve ser exatamente o nome da fila
    #
    # - routing_key="hello": indica que a mensagem será roteada
    #   para a fila chamada "hello"
    #
    # - body=msg: corpo da mensagem (string convertida
    #   automaticamente para bytes pelo pika)
    channel.basic_publish(
        exchange="",
        routing_key="hello",
        body=msg
    )

    # Exibe no console que a mensagem foi enviada com sucesso.
    print(f" [x] Enviado: {msg}")

    # Aguarda 1 segundo antes de enviar a próxima mensagem.
    # Isso facilita a visualização do fluxo no consumer (receiver).
    time.sleep(1)


# Mensagem final informando que todas as mensagens foram enviadas.
print("Mensagens enviadas!")


# Fecha explicitamente a conexão com o RabbitMQ.
# Boa prática para liberar recursos de rede e memória.
connection.close()
