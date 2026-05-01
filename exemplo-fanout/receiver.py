"""
=====================================================
Autor: Saulo Costa

Código educacional voltado à prática e experimentação
do consumo de mensagens com RabbitMQ, utilizando o
protocolo AMQP (Advanced Message Queuing Protocol) e
a biblioteca Pika em Python.

Este módulo implementa um Consumer (Receiver) que:
- Conecta-se a um broker RabbitMQ local
- Autentica-se com credenciais explícitas
- Declara uma exchange do tipo fanout
- Declara e associa uma fila à exchange
- Permanece em escuta contínua, recebendo e processando
  mensagens publicadas
=====================================================
"""

import pika


class RabbitMQConsumer:
    """
    Classe responsável por encapsular toda a lógica de consumo
    de mensagens do RabbitMQ utilizando o Pika.

    Essa abordagem facilita:
    - Reutilização do código
    - Organização da lógica
    - Manutenção e testes
    """

    def __init__(
        self,
        host: str = "localhost",
        username: str = "admin",
        password: str = "admin",
        exchange: str = "logs",
        exchange_type: str = "fanout",
        queue: str = "hello",
    ):
        """
        Inicializa o consumer com os parâmetros de conexão
        e configuração do RabbitMQ.

        :param host: Endereço do broker RabbitMQ
        :param username: Usuário de autenticação
        :param password: Senha do usuário
        :param exchange: Nome da exchange
        :param exchange_type: Tipo da exchange (fanout, direct, topic, headers)
        :param queue: Nome da fila a ser consumida
        """

        self.host = host
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.queue = queue

        # Define explicitamente as credenciais de autenticação.
        # O uso de credenciais próprias evita limitações
        # do usuário padrão "guest".
        self.credentials = pika.PlainCredentials(username, password)

        self.connection = None
        self.channel = None

    def connect(self) -> None:
        """
        Estabelece a conexão com o broker RabbitMQ e
        cria um canal de comunicação.

        - A conexão é um recurso pesado
        - O canal é leve e utilizado para operações AMQP
        """

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.host,
                credentials=self.credentials,
            )
        )

        self.channel = self.connection.channel()

    def setup_infrastructure(self) -> None:
        """
        Declara a exchange, a fila e realiza o bind entre elas.

        Exchange fanout:
        - Distribui mensagens para todas as filas associadas
        - Ignora routing keys
        - Ideal para broadcast (logs, eventos, notificações)
        """

        # Declara a exchange
        self.channel.exchange_declare(
            exchange=self.exchange,
            exchange_type=self.exchange_type,
        )

        # Declara a fila
        result = self.channel.queue_declare(queue=self.queue)

        # Guarda o nome efetivo da fila (útil para filas dinâmicas)
        self.queue_name = result.method.queue

        # Associa a fila à exchange
        self.channel.queue_bind(
            exchange=self.exchange,
            queue=self.queue_name,
        )

    @staticmethod
    def callback(ch, method, properties, body: bytes) -> None:
        """
        Função callback chamada automaticamente
        sempre que uma nova mensagem é entregue ao consumer.

        :param ch: Canal de comunicação
        :param method: Informações da entrega (delivery_tag, exchange, etc.)
        :param properties: Propriedades e metadados AMQP
        :param body: Corpo da mensagem (sempre em bytes)
        """

        print(f" [x] Mensagem recebida: {body}")

    def start_consuming(self) -> None:
        """
        Inicia o consumo contínuo da fila configurada.

        auto_ack=True:
        - A mensagem é confirmada automaticamente
        - Simplifica o fluxo
        - Menos seguro para cenários críticos
        """

        print(" [*] Aguardando mensagens. Pressione CTRL+C para sair")

        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.callback,
            auto_ack=True,
        )

        self.channel.start_consuming()

    def run(self) -> None:
        """
        Orquestra a execução completa do consumer:
        - Conexão
        - Setup da infraestrutura
        - Início do consumo
        """

        self.connect()
        self.setup_infrastructure()
        self.start_consuming()


# Permite que o consumer seja executado diretamente
# via linha de comando: python consumer.py
if __name__ == "__main__":
    consumer = RabbitMQConsumer()
    consumer.run()
