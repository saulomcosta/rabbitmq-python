"""
=====================================================
Autor: Saulo: 01 de maio de 2026Autor: Saulo Costa

Descrição:
Este script foi desenvolvido com fins educacionais e
experimentais, tendo como objetivo demonstrar o consumo
de mensagens utilizando RabbitMQ por meio do protocolo
AMQP, com suporte da biblioteca Pika em Python.

O código atua como um Consumer (Receiver), conectando-se
a um broker RabbitMQ local, autenticando-se com
credenciais específicas, declarando uma fila e
permanecendo em estado de escuta contínua para receber,
processar e confirmar mensagens publicadas nessa fila.
=====================================================
"""

# Importa a biblioteca pika, utilizada como cliente Python
# para comunicação com o RabbitMQ via protocolo AMQP.
#
# O AMQP (Advanced Message Queuing Protocol) define as regras
# de troca de mensagens entre produtores, brokers e consumidores.
import pika

# Importa o módulo time, utilizado aqui para simular
# tempo de processamento das mensagens recebidas.
import time


# Define explicitamente as credenciais de autenticação
# que serão utilizadas para acessar o RabbitMQ.
#
# - "admin" representa o usuário configurado no broker
# - "admin" representa a senha correspondente
#
# O uso de credenciais explícitas é uma boa prática,
# evitando limitações do usuário padrão "guest".
credentials = pika.PlainCredentials("admin", "admin")


# Estabelece uma conexão com o servidor RabbitMQ.
#
# BlockingConnection:
# - Mantém a conexão ativa enquanto o script estiver em execução
# - Opera de forma síncrona, aguardando resposta do broker
#
# ConnectionParameters define:
# - host="localhost": o broker está sendo executado localmente
# - credentials=credentials: credenciais usadas na autenticação
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="localhost",
        credentials=credentials
    )
)


# Cria um canal de comunicação dentro da conexão.
#
# Conceito importante:
# - A conexão é um recurso mais pesado
# - Os canais são leves e devem ser usados para
#   publicar e consumir mensagens
channel = connection.channel()


# Declara a fila chamada "hello".
#
# Comportamento do RabbitMQ:
# - Caso a fila não exista, ela será criada automaticamente
# - Caso já exista, será reutilizada
#
# Isso garante que o consumer possa ser iniciado
# mesmo antes do producer enviar mensagens.
channel.queue_declare(queue="hello")


# Define a função de callback.
#
# Essa função é chamada automaticamente sempre que
# uma nova mensagem for entregue à fila "hello".
#
# Parâmetros recebidos:
# - ch: canal pelo qual a mensagem foi entregue
# - method: informações sobre a entrega (delivery_tag)
# - properties: metadados e propriedades da mensagem
# - body: corpo da mensagem (recebido como bytes)
def callback(ch, method, properties, body):

    # Exibe o conteúdo da mensagem recebida.
    print(f" [x] Recebido {body}")

    # Simula um tempo de processamento da mensagem.
    time.sleep(1)

    # Indica que o processamento da mensagem foi concluído.
    print(" [x] Processamento concluído")

    # Envia a confirmação manual (ack) ao RabbitMQ,
    # informando que a mensagem foi processada com sucesso.
    ch.basic_ack(delivery_tag=method.delivery_tag)


# Configura o consumo da fila.
#
# Parâmetros:
# - queue="hello": fila que será consumida
# - on_message_callback=callback: função chamada ao receber mensagens
# - auto_ack=False:
#   → exige confirmação manual da mensagem
#   → evita perda de mensagens em caso de falha
#   → recomendado para cenários mais críticos
channel.basic_consume(
    queue="hello",
    on_message_callback=callback,
    auto_ack=False
)


# Mensagem exibida no terminal indicando que o consumer
# está ativo e aguardando mensagens.
print(" [*] Aguardando mensagens. Pressione CTRL+C para sair")


# Inicia o loop de consumo.
#
# A partir deste ponto:
# - O script permanece em execução contínua
# - Fica escutando a fila "hello"
# - Executa o callback para cada nova mensagem recebida
#
# O encerramento do programa ocorre apenas
# quando o usuário pressionar CTRL+C.
channel.start_consuming()
