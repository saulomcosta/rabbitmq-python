"""
=====================================================
acionais eAutor: Saulo Costa
experimentais, com o objetivo de demonstrar o consumo
de mensagens utilizando RabbitMQ e o protocolo AMQP,
por meio da biblioteca Pika em Python.

O script atua como um Consumer (Receiver), conectando-se
a um broker RabbitMQ local, autenticando-se com usuário
e senha específicos, declarando uma fila e permanecendo
em estado de escuta para receber e processar mensagens
publicadas nessa fila.
=====================================================
"""

# Importa a biblioteca pika, que é o cliente oficial mais utilizado
# em Python para comunicação com o RabbitMQ via protocolo AMQP.
#
# O AMQP (Advanced Message Queuing Protocol) define como produtores,
# brokers e consumidores trocam mensagens de forma confiável.
import pika


# Cria explicitamente as credenciais de autenticação
# que serão usadas para se conectar ao RabbitMQ.
#
# - "admin" é o usuário criado no RabbitMQ
# - "admin" é a senha associada a esse usuário
#
# O uso de credenciais explícitas é uma boa prática e
# evita as restrições impostas ao usuário padrão "guest".
credentials = pika.PlainCredentials("admin", "admin")


# Estabelece uma conexão com o servidor RabbitMQ.
#
# BlockingConnection:
# - Mantém a conexão ativa enquanto o programa estiver rodando
# - Cada operação aguarda resposta do servidor (modo síncrono)
#
# ConnectionParameters define:
# - host="localhost": o broker RabbitMQ está rodando localmente
# - credentials=credentials: autenticação com usuário e senha
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="localhost",
        credentials=credentials
    )
)


# Cria um canal (channel) dentro da conexão.
#
# Conceito importante:
# - A conexão é um recurso caro
# - Os canais são leves e recomendados para comunicação
# - Sempre publicamos e consumimos mensagens por meio de canais
channel = connection.channel()


# Declara a fila chamada "hello".
#
# Comportamento do RabbitMQ:
# - Se a fila não existir, ela será criada
# - Se já existir, será reutilizada
#
# Isso garante que o consumer não falhe caso a fila
# ainda não tenha sido criada pelo producer.
channel.queue_declare(queue="hello")


# Define a função callback que será chamada automaticamente
# toda vez que uma nova mensagem for entregue à fila "hello".
#
# Parâmetros da função:
# - ch: objeto do canal
# - method: informações sobre a entrega da mensagem
# - properties: propriedades AMQP (headers, metadata, etc.)
# - body: corpo da mensagem (sempre recebido como bytes)
def callback(ch, method, properties, body):

    # Exibe o conteúdo da mensagem recebida no console.
    # O body é exibido como bytes (ex: b'Mensagem'),
    # pois o AMQP transmite dados nesse formato.
    print(f" [x] Recebido {body}")


# Configura o consumidor da fila.
#
# Parâmetros:
# - queue="hello": define qual fila será consumida
# - on_message_callback=callback: função chamada ao receber mensagem
# - auto_ack=True:
#   → o RabbitMQ considera a mensagem processada automaticamente
#   → não há confirmação manual (ack)
#   → simples, porém menos seguro em cenários críticos
channel.basic_consume(
    queue="hello",
    on_message_callback=callback,
    auto_ack=True
)


# Mensagem exibida no terminal para indicar que o consumer
# está ativo e aguardando novas mensagens.
print(" [*] Aguardando mensagens. Pressione CTRL+C para sair")


# Inicia o loop de consumo.
#
# A partir deste ponto:
# - O script entra em execução contínua
# - Fica escutando a fila "hello"
# - Executa o callback sempre que uma mensagem chegar
#
# O programa só será finalizado quando o usuário
# pressionar CTRL+C no terminal.
channel.start_consuming()
