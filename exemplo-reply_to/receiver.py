"""=====================================================
Autor: Saulo Costa

Descrição:
Implementação educacional de um Consumer RPC utilizando
RabbitMQ, o protocolo AMQP (Advanced Message Queuing Protocol)
e a biblioteca Pika em Python.

Este script atua como um Consumer (Receiver) e:
- Conecta-se a um broker RabbitMQ local
- Autentica-se com credenciais explícitas
- Declara uma fila RPC
- Aguarda requisições enviadas por um Producer
- Processa a mensagem recebida
- Retorna a resposta utilizando reply_to e correlation_id

O padrão RPC em mensageria:
- Producer envia a requisição
- Consumer executa o processamento
- Consumer responde via fila temporária do Producer
- correlation_id garante a associação correta da resposta

Conceitos abordados:
- AMQP (Queue, Routing Key)
- RPC sobre RabbitMQ
- reply_to e correlation_id
- Consumer síncrono com BlockingConnection
=====================================================
"""

import pika


class RpcConsumer:
    """
    Classe responsável por consumir requisições RPC,
    processá-las e retornar respostas ao Producer.
    """

    def __init__(self):
        """
        Inicializa a conexão, o canal e a fila RPC.
        """

        # Credenciais explícitas para autenticação
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

        # Declara a fila RPC (deve existir no Producer)
        self.channel.queue_declare(queue="rpc.queue")

        # Define consumo da fila RPC
        self.channel.basic_consume(
            queue="rpc.queue",
            on_message_callback=self.on_request
        )

        print(" [x] Aguardando requisições RPC...")

    def on_request(self, ch, method, properties, body):
        """
        Processa a mensagem recebida e envia a resposta
        para a fila indicada no reply_to.
        """

        n = int(body)
        print(f" [*] Processando requisição: {n} * {n}")

        response = n * n

        # Publica a resposta para o Producer
        ch.basic_publish(
            exchange="",
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id
            ),
            body=str(response)
        )

        # Confirma o processamento da mensagem
        ch.basic_ack(delivery_tag=method.delivery_tag)

        print(" [✓] Resposta enviada")

    def start(self):
        """
        Inicia o loop de consumo bloqueante.
        """
        self.channel.start_consuming()

    def close(self):
        """
        Encerra corretamente a conexão.
        """
        self.connection.close()

# =====================================================
# Execução do Consumer RPC
# =====================================================
if __name__ == "__main__":
    consumer = RpcConsumer()
    try:
        consumer.start()
    except KeyboardInterrupt:
        print("\n [!] Consumer finalizado pelo usuário")
        consumer.close()
