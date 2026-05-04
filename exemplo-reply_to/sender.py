"""
=====================================================
Autor: Saulo Costa

Descrição:
O objetivo deste código é demonstrar, de forma prática,
como funciona a comunicação RPC (Remote Procedure Call)
assíncrona baseada em mensageria.

Este Producer:
- Envia uma mensagem para uma fila RPC
- Cria automaticamente uma fila exclusiva de resposta
- Aguarda o retorno do Consumer utilizando correlation_id

Conceitos abordados:
- AMQP (Exchange, Queue, Routing Key)
- RPC sobre mensageria
- correlation_id e reply_to
- Callback assíncrono com Pika
=====================================================
"""

import pika
import uuid


class RpcProducer:
    """
    Classe responsável por enviar requisições RPC através do RabbitMQ
    e aguardar respostas utilizando uma fila exclusiva de callback.
    """

    def __init__(self):
        """
        Inicializa a conexão, o canal e a fila de resposta RPC.
        """

        # Identificador da requisição atual
        self.corr_id = None

        # Credenciais explícitas (evita restrição do usuário guest)
        credentials = pika.PlainCredentials(
            username="admin",
            password="admin"
        )

        # Conexão com o RabbitMQ
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host="localhost",
                credentials=credentials
            )
        )

        # Canal AMQP
        self.channel = self.connection.channel()

        # Fila exclusiva e temporária para receber respostas
        result = self.channel.queue_declare(
            queue="",
            exclusive=True
        )
        self.callback_queue = result.method.queue

        # Consumer que escuta respostas RPC
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )

        print(f" [x] Aguardando resposta na fila: {self.callback_queue}")

    def on_response(self, ch, method, props, body):
        """
        Executado automaticamente ao receber uma mensagem
        na fila de callback.
        """

        if props.correlation_id == self.corr_id:
            print(f" [✓] Resposta recebida: {body.decode()}")
            self.channel.stop_consuming()

    def call(self, message: str):
        """
        Envia uma requisição RPC ao consumer.

        :param message: mensagem enviada para processamento
        """

        self.corr_id = str(uuid.uuid4())

        self.channel.basic_publish(
            exchange="",
            routing_key="rpc.queue",
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id
            ),
            body=message
        )

        print(f" [→] Requisição enviada (correlation_id={self.corr_id})")

        self.channel.start_consuming()

    def close(self):
        """Finaliza a conexão com o RabbitMQ."""
        self.connection.close()

# =====================================================
# Execução do Producer RPC
# =====================================================
if __name__ == "__main__":
    producer = RpcProducer()
    try:
        producer.call("30")
    finally:
        producer.close()
