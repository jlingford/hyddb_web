import pika

try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()
    print("Successfully connected to RabbitMQ!")
    connection.close()
except Exception:
    print("Failed to connect to RabbitMQ")
